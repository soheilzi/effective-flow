if [ $# -lt 4 ]
then
    echo "usage: $0 <data count> <outputfile> <sample size> <prune count>"
    exit
fi

for i in `seq 1 $1`
do
    network_dir=$(date +'%d/%H/%M')

    echo "\nstart----gen $i\n"
    
    echo "\n-------simulation start $i\n"
    cd ./cloth
    bash ./run-simulation.sh 10 output_dir/
    cd ..
    echo "\n-------simulation end $i\n" 

    echo "-------ef calculation start $i"
    python3 ef.py $3 ./cloth/edges_ef.csv ./cloth/nodes_ef.csv ./cloth/output_dir/cloth_output.json $2
    echo "-------ef calculation end $i"
    
    cd ./result/networks/
    mkdir $network_dir
    cp ../../cloth/edges_ef.csv ./$network_dir
    cp ../../cloth/channels_ef.csv ./$network_dir
    cd ../../

    echo "\n-------prune start $i\n"
    python3 prunenet.py $4 ./cloth/channels_ef.csv ./cloth/edges_ef.csv
    echo "\n-------prune end $i\n"

    echo "\nend------gen $i\n"
done