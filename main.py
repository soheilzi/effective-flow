import networkx as nx
import multiprocessing
import pandas as pd
import matplotlib.pyplot as plt
import pylab
import random
import numpy as np
import time

sampleSize = 256
processCount = 4
X = [[multiprocessing.Value("f", 0.0, lock=False) for j in range(sampleSize // processCount)] for i in range(processCount)]

def efSampler(G, randS, randT, processId, costCoef=1):
    # print("%d, size = %d"% (processId, len(randS)))
    for i in range(sampleSize // processCount):
        # print("%d, i = %d"% (processId, i))
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
        X[processId][i].value = (mincostFlowValue - costCoef * mincost) / fund
        # print(X[processId][i])
    

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

# multiprocessing
randS = random.sample(nodeList, sampleSize)
randT = random.sample(nodeList, sampleSize)

# pool = processPool(processCount)
# r = pool.map(efSampler, (G, randS[0:sampleSize // processCount], randT[0:sampleSize // processCount], 0,))
# pool.close()
# pool.join()

p0 = multiprocessing.Process(target=efSampler, args=(G, randS[0:sampleSize // processCount], randT[0:sampleSize // processCount], 0,))
p1 = multiprocessing.Process(target=efSampler, args=(G, randS[sampleSize // processCount: 2 * sampleSize // processCount], randT[sampleSize // processCount: 2 * sampleSize // processCount], 1,))
p2 = multiprocessing.Process(target=efSampler, args=(G, randS[sampleSize // 2: 3 * sampleSize // processCount], randT[sampleSize // 2: 3 * sampleSize // processCount], 2,))
p3 = multiprocessing.Process(target=efSampler, args=(G, randS[3 * sampleSize // processCount: sampleSize], randT[3 * sampleSize // processCount: sampleSize], 3,))

p0.start()
p1.start()
p2.start()
p3.start()

p0.join()
p1.join()
p2.join()
p3.join()

Xjoined = []
for i in range(processCount):
    for j in range(sampleSize // processCount):
        Xjoined.append(X[i][j].value)

print("overall std :", (np.std(Xjoined) / np.sqrt(sampleSize)))
print("Lightning network EF :", np.mean(Xjoined))