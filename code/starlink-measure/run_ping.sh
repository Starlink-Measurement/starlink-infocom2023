#!/usr/bin/env bash
show_help() {
    echo "Usage: $0 [-n] path/to/dest_measurement_folder"
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

dest_fold="$1"
MAX_RETRY=10

unique_fname() {
    name=$1
    count=1

    timestamp=$(date -u +"%Y-%m-%d_%H-%M-%S")
    fname="${name}.${timestamp}.csv"

    echo "$fname"
}

destroy_instances() {
    (cd instances; terraform destroy -auto-approve)
}

# 9 regions
regions=(ap-southeast-2 ap-southeast-1 ap-northeast-1 ap-south-1 eu-west-2 me-south-1 sa-east-1 us-west-1 af-south-1)
#regions=(ap-southeast-2 us-west-1)

if [ "$no_instances" != true ]; then
    ./gen_main_tf.py "${regions[@]}"
    ./spin_instances.sh
    trap destroy_instances EXIT # Destroy instances on exit for any reason
fi

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

    dest_path="${dest_fold}/${region_name}"
    echo "Saving to dir $dest_path"
    mkdir -p "${dest_path}"

    name="${dest_path}/ping_${region}"
    fname="$(unique_fname ${name})"

    ./ping-csv.sh --add-timestamp -4 "${instance_ip}" > "${fname}" &
done

wait
