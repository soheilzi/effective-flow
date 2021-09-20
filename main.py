import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import pylab
import random
import numpy as np
import threading
import time

sampleSize = 64
threadCount = 4
X = [[0 for j in range(sampleSize // threadCount)] for i in range(threadCount)]

def efSampler(G, randS, randT, threadId, costCoef=1):
    for i in range(sampleSize // threadCount):
        s, t = randS[i], randT[i]
        mincostFlow = nx.max_flow_min_cost(G, s, t)
        mincost = nx.cost_of_flow(G, mincostFlow)
        mincost /= 1000000
        mincostFlowValue = sum((mincostFlow[u][t] for u in G.predecessors(t))) - sum(
            (mincostFlow[t][v] for v in G.successors(t))
        )
        
        fund = sum((G[s][u]['capacity'] for u in G.successors(s)))
        if fund == 0:
            continue
        X[threadId][i] = (mincostFlowValue - costCoef * mincost) / fund
    

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

# multithreading
randS = random.sample(nodeList, sampleSize)
randT = random.sample(nodeList, sampleSize)

t0 = threading.Thread(target=efSampler, args=(G, randS[0:sampleSize // 4], randT[0:sampleSize // 4], 0,))
t1 = threading.Thread(target=efSampler, args=(G, randS[sampleSize // 4: sampleSize // 2], randT[sampleSize // 4: sampleSize // 2], 1,))
t2 = threading.Thread(target=efSampler, args=(G, randS[sampleSize // 2: 3 * sampleSize // 4], randT[sampleSize // 2: 3 * sampleSize // 4], 2,))
t3 = threading.Thread(target=efSampler, args=(G, randS[3 * sampleSize // 4: sampleSize], randT[3 * sampleSize // 4: sampleSize], 3,))

t0.start()
t1.start()
t2.start()
t3.start()

t0.join()
t1.join()
t2.join()
t3.join()

Xjoined = sum(X, [])
print("overall std :", np.std(Xjoined) / np.sqrt(sampleSize))
print("Lightning network EF :", np.mean(Xjoined))