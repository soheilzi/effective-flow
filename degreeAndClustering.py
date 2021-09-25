import networkx as nx
import pandas as pd
import numpy as np
import sys

edgesDir = sys.argv[1]
nodesFile = sys.argv[2]


for i in range(1, 30):
        edgesFile = edgesDir + str(i) + "/edges_ef.csv"

        data = pd.read_csv(edgesFile)
        data.rename(columns={"balance" : "capacity", "fee_proportional" : "weight"}, inplace=True)
        data = data[['from_node_id', 'to_node_id', 'capacity', 'weight']]

        nodeData = pd.read_csv(nodesFile)
        nodeList = list(nodeData['id'])

        ### preprocess
        data = data.groupby(['from_node_id', 'to_node_id']).agg({'capacity': 'sum', 'weight': 'mean'}).reset_index()
        data = data.astype({'weight' : int})

        ### graph constructoin
        G = nx.from_pandas_edgelist(data, 'from_node_id', 'to_node_id', edge_attr=['capacity', 'weight'], create_using=nx.DiGraph())
        G.add_nodes_from(nodeList)


        average_clustering = nx.average_clustering(G)
        transitivity = nx.transitivity(G)

        print("%d,%f,%f,%f"% (i, average_clustering, transitivity, np.average(list(G.degree), axis=0)[1]))
