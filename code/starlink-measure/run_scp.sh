#!/usr/bin/env bash
show_help() {
    echo "$0 [-n] path/to/dest_measurement_folder"
}

OPTIND=1 # Reset in case getopts has been used previously in the shell.

while getopts "h?n" opt; do
   case "$opt" in
      h|\?) # display Help
         show_help
         exit 0
         ;;
     n) # Turns off starting up instances
         no_instances=true
         ;;
   esac
done

shift $((OPTIND-1))

if [ $# -eq 0 ]; then
    show_help
    exit 1
fi

# For raspberry pi crontab
if [[ "$(uname -m)" == "armv7l" ]]; then
    export PATH=/home/pi/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/games:/usr/games
fi

dest_fold="$1"
MAX_RETRY=10

unique_fname() {
    name=$1
    count=1

    timestamp=$(date -u +"%Y-%m-%d_%H-%M-%S")
    fname="${name}.${timestamp}.csv"

    echo "$fname"
}

run_scp_down() {
    instance_ip=$1
    mb=$2

    ( set -e

    TIMEFORMAT='%R' # Required to grab time
    out=$({ time scp -o "StrictHostKeyChecking=accept-new" terraform@${instance_ip}:test_${mb}M.img . ; } |& egrep ^[0-9]+.[0-9]+)
    echo -n "$out"
    )
}

run_scp_up() {
    instance_ip=$1
    mb=$2
    
    ( set -e

    TIMEFORMAT='%R' # Required to grab time
    fallocate -l ${mb}M test_${mb}M.img
    out=$({ time scp -o "StrictHostKeyChecking=accept-new" test_${mb}M.img terraform@${instance_ip}: ; } |& egrep ^[0-9]+.[0-9]+)
    echo -n "$out"
    )
}

run_iperf() {
    instance_ip=$1
    dest_path="$2"
    region="$3"
    length=$4

    ( set -e # Subshell to exit on first error

    name="${dest_path}/${region}_scp"
    fname_down="${name}_down.csv"
    fname_up="${name}_up.csv"

    sizes=(1 10 100 200 300)
    headers="timestamp,region,1MB,10MB,100MB,200MB,300MB"
    timestamp=$(date -u +"%s")
    echo "Running SCP measurements"
    if [ ! -f "$fname_down" ]; then
        echo "$headers" > "$fname_down"
    else
        echo '' >> "$fname_down"
    fi
    if [ ! -f "$fname_up" ]; then
        echo "$headers" > "$fname_up"
    else
        echo '' >> "$fname_up"
    fi
    echo -n "${timestamp}," >> "$fname_down"
    echo -n "${timestamp}," >> "$fname_up"
    echo -n "${region}," >> "$fname_down"
    echo -n "${region}," >> "$fname_up"

    scp_up_time=$(run_scp_up $instance_ip ${sizes[0]})
    echo -n "${scp_up_time}," >> "$fname_up"

    for i in $(seq 0 $(expr ${#sizes[@]} - 2)); do 
        scp_down_time=$(run_scp_down $instance_ip ${sizes[i]} &)
        
        next_id=$(expr ${i} + 1)
        forward=${sizes[next_id]}
        scp_up_time=$(run_scp_up $instance_ip $forward)
        echo -n "${scp_up_time}," >> "$fname_up"

        wait # In case download is slower
        echo -n "${scp_down_time}," >> "$fname_down"
        echo "Finished ${sizes[i]} MB"
    done

    scp_down_time=$(run_scp_down $instance_ip ${sizes[-1]})
    echo -n "$scp_down_time" >> "$fname_down"

    sleep 3 # Wait before next test
    )
}

destroy_instances() {
    (cd instances; terraform destroy -auto-approve)
}

# 9 regions
regions=(ap-southeast-2 ap-southeast-1 ap-northeast-1 ap-south-1 eu-west-2 me-south-1 sa-east-1 us-west-1 af-south-1)
#regions=(ap-southeast-2 us-west-1)

./gen_main_tf.py "${regions[@]}"

if [ "$no_instances" != true ]; then
    (cd instances; terraform init)
    (cd instances; terraform apply -auto-approve) # Long spin up of instances
    trap destroy_instances EXIT # Destroy instances on exit for any reason
fi

#./run_ping.sh -n "${dest_fold}_ping" &

for region in "${regions[@]}"; do 
    instance_ip="$(cd instances; terraform output -raw ${region}_public_ip)"
    region_raw="$(cd instances; terraform output -raw ${region}_region_name)"

    region_no_spaces="${region_raw// /_}" # Replace spaces with underscores
    region_name="${region_no_spaces//[^[:alnum:]_]/}" # Remove special charas except underscores

    dest_path="${dest_fold}/${region_name}"
    echo "Saving to dir $dest_path"
    mkdir -p "${dest_path}"

    echo "Attempting to run iperf3 for $length seconds"

    err=1
    count=0
    until [ "$err" == 0 ] && [ "$count" -lt "$MAX_RETRY" ]; do
        # Must be run separately to properly exit the subshell upon error
        run_iperf "$instance_ip" "$dest_path" "$region" $length
        err=$?
        if [ "$err" != 0 ]; then
            echo "Error. Sleeping and trying again..."
            sleep 10
            echo "Restarting..."
            ((count++))
        fi
    done

    echo "Logged measurements to the following:"
    echo "$fname"

    if [ "$count" -ge "$MAX_RETRY" ]; then
        echo "ERROR: Max Retries reached. Quitting measurements."
    fi

    sleep 3
done
