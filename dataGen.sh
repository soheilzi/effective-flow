if [ $# -lt 4 ]
then
    echo "usage: $0 <data count> <outputfile> <sample size> <prune count>"
    exit
fi

for i in `seq 1 $1`
do
    echo "start----gen $i"
    
    echo "-------simulation start $i"
    cd ./cloth
    bash ./run-simulation.sh 10 output_dir/
    cd ..
    echo "-------simulation end $i" 

    echo "-------ef calculation start $i"
    python3 ef.py $3 ./cloth/edges_ef.csv ./cloth/nodes_ef.csv ./cloth/output_dir/cloth_output.json $2
    echo "-------ef calculation end $i"
    
    echo "-------prune start $i"
    python3 prunenet.py $4 ./cloth/channels_ef.csv ./cloth/edges_ef.csv
    echo "-------prune end $i"

    echo "end------gen $i"
done