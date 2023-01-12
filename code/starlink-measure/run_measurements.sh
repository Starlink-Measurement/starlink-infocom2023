#!/usr/bin/env bash
export PATH=/home/pi/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/games:/usr/games
cleanup() {
    kill -2 $1
    wait
    exit
}

output=starlink
MAX_MEASURE=200
MAX_RETRY=180

(cd /home/pi/Starlink/starlink-measure; ./run_ping.sh "../${output}_ping" &> /home/pi/Starlink/ping_measure.log) &
ping_pid=$!
trap "cleanup $ping_pid" EXIT SIGTERM

count=0
while ! (cd /home/pi/Starlink/starlink-measure/instances/; ping -c 1 -n `terraform output -raw us-west-1_public_ip 2> /dev/null` &> /dev/null)
do
    [ "$count" -lt "$MAX_RETRY" ] || exit 1
    printf "%c" "."
    sleep 1
    ((count++))
done

for val in {1..$MAX_MEASURE}
do
    (cd /home/pi/Starlink/starlink-measure; ./run_world_iperf3.sh -n "../${output}_iperf3" &> /home/pi/Starlink/measure.log)
    sleep 1
done
