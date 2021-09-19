import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import pylab
import random
import numpy as np
import threading
import time

data = pd.read_csv("cloth/edges_ln.csv")
data.rename(columns={"balance" : "capacity", "fee_proportional" : "weight"}, inplace=True)
data = data[['from_node_id', 'to_node_id', 'capacity', 'weight']]

nodeData = pd.read_csv("cloth/nodes_ln.csv")
nodeList = list(nodeData['id'])

### preprocess
data = data.groupby(['from_node_id', 'to_node_id']).agg({'capacity': 'sum', 'weight': 'mean'}).reset_index()
data = data.astype({'weight' : int})

### graph constructoin
G = nx.from_pandas_edgelist(data, 'from_node_id', 'to_node_id', edge_attr=['capacity', 'weight'], create_using=nx.DiGraph())

### sampling
# sampleSize = 50
# randS = random.sample(nodeList, sampleSize)
# randT = random.sample(nodeList, sampleSize)

def efSampler(G, sampleS, sampleT, costCoef=1):
    X = []
    sampleSize = len(sampleS)
    for i in range(sampleSize):
        s, t = randS[i], randT[i]
        mincostFlow = nx.max_flow_min_cost(G, s, t)
        mincost = nx.cost_of_flow(G, mincostFlow)
        mincost /= 1000000
        mincostFlowValue = sum((mincostFlow[u][t] for u in G.predecessors(t))) - sum(
            (mincostFlow[t][v] for v in G.successors(t))
        )
        
        fund = sum((G[s][u]['capacity'] for u in G.successors(s)))
        if fund == 0:
            X.append(0)
            continue
        X.append((mincostFlowValue - costCoef * mincost) / fund)


    # save to file
    print("overall std :",np.std(X) / np.sqrt(sampleSize))
    print("Lightning network EF :", np.mean(X))

# multithreading
class myThread
