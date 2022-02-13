#!/bin/bash          



if [ $# -lt 3 ]
then
    echo "usage: $0 <starting iter> <ending iter> <unbalance count>"
    exit
fi
unbalance_count=$3
# we have 30457 channels in the channels file if we want 20 datapoints we can eliminate 1500 extra channels per iteration
#1500 channels per iteration
for i in `seq $1 $2`
do
    network_dir=$((i*unbalance_count)) 

    echo "start----gen $i with $((i*unbalance_count)) channels becomming unbalanced"
    
    echo "-------start unbalancing at" $(date +'%d//%H:%M:%S')

    cd Unbalancing_effect
    python3 betweenness_unbalancer.py $((i*unbalance_count)) ../cloth/channels_ln.csv ../cloth/edges_ln.csv
    cd ..

    echo "-------end unbalancing at" $(date +'%d//%H:%M:%S')


    echo "-------simulation start $i at" $(date +'%d//%H:%M:%S')
    cd ./cloth
    bash ./run-simulation.sh 10 output_dir/
    cd ..
    echo "-------simulation end $i at" $(date +'%d//%H:%M:%S')

    
    cd ./ub_results/EBC_networks/
    mkdir $network_dir
    cp ../../cloth/edges_ub.csv ./$network_dir
    cp ../../cloth/output_dir/cloth_output.json ./$network_dir
    cd ../../

    echo "end------gen $i"
done