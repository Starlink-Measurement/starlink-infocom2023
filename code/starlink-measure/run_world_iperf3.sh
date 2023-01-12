#!/usr/bin/env bash
show_help() {
    echo "$0 [-n] path/to/dest_measurement_folder"
}

bits_down=88M
bits_up=15M

OPTIND=1 # Reset in case getopts has been used previously in the shell.

while getopts "h?nd:u:" opt; do
   case "$opt" in
      h|\?) # display Help
         show_help
         exit 0
         ;;
     n) # Turns off starting up instances
         no_instances=true
         ;;
     d) # UDP bits download bandwidth
         bits_down="$OPTARG"
         ;;
     u) # UDP bits upload bandwidth
         bits_up="$OPTARG"
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
length=30
CLIENT=client
SERVER=server
MAX_RETRY=10

unique_fname() {
    name=$1
    count=1

    timestamp=$(date -u +"%Y-%m-%d_%H-%M-%S")
    fname="${name}.${timestamp}.log"

    echo "$fname"
}

run_tcp() {
    instance_ip=$1
    fname_down="$2"
    fname_up="$3"
    length=$4

    ( set -e

    echo "Running TCP measurements"
    iperf3 -c "$instance_ip" -R -Z -t $length -P 4 -J > "$fname_down" & 
    iperf3 -c "$instance_ip" -p 5202 -Z -t $length -P 4 -J > "$fname_up"
    wait
    )
}

run_udp() {
    instance_ip=$1
    fname_down="$2"
    fname_up="$3"
    length=$4

    ( set -e

    echo "Running UDP measurements"
    iperf3 -c "$instance_ip" -R -Z -t $length -u -b $bits_down -P 4 -J > "$fname_down" & 
    iperf3 -c "$instance_ip" -p 5202 -Z -t $length -u -b $bits_up -P 4 -J > "$fname_up"
    wait
    )
}

run_iperf() {
    instance_ip=$1
    fname_down=("$2" "$4")
    fname_up=("$3" "$5")
    length=$6

    funcs=(run_tcp run_udp)
    #funcs=(run_udp)

    for i in ${!funcs[@]}; do
        err=1
        count=0
        until [ "$err" == 0 ] || [ "$count" -ge "$MAX_RETRY" ]; do
            # Must be run separately to properly exit the subshell upon error
            ${funcs[$i]} $instance_ip "${fname_down[$i]}" "${fname_up[$i]}" $length
            err=$?
            if [ "$err" != 0 ]; then
                echo "Error. Sleeping and trying again..."
                sleep 10
                echo "Restarting..."
                ((count++))
            fi
        done

        sleep 1 # Wait before next test
    done
}

destroy_instances() {
    (cd instances; terraform destroy -auto-approve)
}

# 9 regions
regions=(ap-southeast-2 ap-southeast-1 ap-northeast-1 ap-south-1 eu-west-2 me-south-1 sa-east-1 us-west-1 af-south-1)
#regions=(ap-southeast-2 us-west-1)
#regions=(us-west-1)

if [ "$no_instances" != true ]; then
    ./gen_main_tf.py --me "t3.medium" "${regions[@]}"
    ./spin_instances.sh
    trap destroy_instances EXIT # Destroy instances on exit for any reason
fi

#./run_ping.sh -n "${dest_fold}_ping" &

for region in "${regions[@]}"; do 
    count=0
    while true; do
        instance_ip="$(cd instances; terraform output -raw ${region}_public_ip)"
        [[ "$instance_ip" =~ ^([0-9]+\.){2}[0-9]+ ]] && break
        [ "$count" -lt "$MAX_RETRY" ] || exit 1
        echo "Failed to get $region IP. Retrying..."
        sleep 1
        ((count++))
    done

    region_raw="$(cd instances; terraform output -raw ${region}_region_name)"

    region_no_spaces="${region_raw// /_}" # Replace spaces with underscores
    region_name="${region_no_spaces//[^[:alnum:]_]/}" # Remove special charas except underscores

    dest_path="${dest_fold}/${region_name}/${CLIENT}"
    echo "Saving to dir $dest_path"
    mkdir -p "${dest_path}"
    name="${dest_path}/${region}_throughput_client_p4"

    echo "Attempting to run iperf3 for $length seconds"

    fname_down="$(unique_fname ${name}_down)"
    fname_up="$(unique_fname ${name}_up)"
    fname_down_udp="$(unique_fname ${name}_down_udp)"
    fname_up_udp="$(unique_fname ${name}_up_udp)"

    run_iperf "$instance_ip" "$fname_down" "$fname_up" "$fname_down_udp" "$fname_up_udp" $length

    echo "Logged measurements to the following:"
    echo "$fname_down"
    echo "$fname_up"

    if [ "$count" -ge "$MAX_RETRY" ]; then
        echo "ERROR: Max Retries reached. Quitting measurements."
    fi

    ssh_host="terraform@${instance_ip}"
    dest_server_path="${dest_fold}/${region_name}/${SERVER}/"
    mkdir -p "$dest_server_path"
    scp -o "StrictHostKeyChecking=accept-new" ${ssh_host}:*.log "$dest_server_path"
done
