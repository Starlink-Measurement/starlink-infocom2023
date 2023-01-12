./spin_instances.sh
echo "running"
instance_ip="$(cd instances; terraform output -raw us-west-1_public_ip)"
down=200695
up=25093
prefix=terrestrial

./run_world_iperf3.sh -n -d ${down}K -u ${up}K ../packet_full_2022-07-23_${prefix}_iperf3
./run_world_iperf3.sh -n -d $(((${down}+1)/2))K -u $(((${up}+1)/2))K ../packet_half_2022-07-23_${prefix}_iperf3
./run_world_iperf3.sh -n -d $(((${down}+2)/3))K -u $(((${up}+2)/3))K ../packet_third_2022-07-23_${prefix}_iperf3
./run_world_iperf3.sh -n -d $(((${down}+3)/4))K -u $(((${up}+3)/4))K ../packet_quarter_2022-07-23_${prefix}_iperf3
./run_world_iperf3.sh -n -d $(((${down}+4)/5))K -u $(((${up}+4)/5))K ../packet_fifth_2022-07-23_${prefix}_iperf3

(cd instances; terraform destroy -auto-approve)
