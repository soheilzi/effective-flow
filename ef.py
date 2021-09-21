import networkx as nx
import multiprocessing
import pandas as pd
import random
import numpy as np
import sys
import json
import csv

sampleSize = int(sys.argv[1])
edgesFile = sys.argv[2]
nodesFile = sys.argv[3]
jsonFile = sys.argv[4]
resultFile = sys.argv[5]

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
    
def readSimResultFile(jsonFile):
    f = open(jsonFile,)
    data = json.load(f)
    f.close()
    # print(data)
    return data

def writeResultIntoFile(resultFile, jsonData, netEf, netEfConf):
    # net_ef,net_ef_conf,success,success_conf,fail_no_path,fail_no_path_conf,fail_no_balance,fail_no_balance_conf,time,time_conf,attempts,attempts_conf,rout_length,rout_length_conf
    row = [netEf, netEfConf, 
    jsonData['Success']['Mean'], (float(jsonData['Success']['ConfidenceMin']) - float(jsonData['Success']['ConfidenceMin']))/2, 
    jsonData['FailNoPath']['Mean'], (float(jsonData['FailNoPath']['ConfidenceMin']) - float(jsonData['FailNoPath']['ConfidenceMin']))/2, 
    jsonData['FailNoBalance']['Mean'], (float(jsonData['FailNoBalance']['ConfidenceMin']) - float(jsonData['FailNoBalance']['ConfidenceMin']))/2, 
    jsonData['Time']['Mean'], (float(jsonData['Time']['ConfidenceMin']) - float(jsonData['Time']['ConfidenceMin']))/2, 
    jsonData['Attempts']['Mean'], (float(jsonData['Attempts']['ConfidenceMin']) - float(jsonData['Attempts']['ConfidenceMin']))/2, 
    jsonData['RouteLength']['Mean'], (float(jsonData['RouteLength']['ConfidenceMin']) - float(jsonData['RouteLength']['ConfidenceMin']))/2, 
    ]
    with open(resultFile, 'a') as f:
        writer = csv.writer(f)
        writer.writerow(row)

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

# multiprocessing
randS = random.sample(nodeList, sampleSize)
randT = random.sample(nodeList, sampleSize)

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


writeResultIntoFile(resultFile, readSimResultFile(jsonFile), np.mean(Xjoined), 2 * (np.std(Xjoined) / np.sqrt(sampleSize)))