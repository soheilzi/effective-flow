import networkx as nx
import multiprocessing
import pandas as pd
import random
import numpy as np
import sys
import json
import csv

sampleSize = int(sys.argv[1]) #32
dataSize = int(sys.argv[2]) #5
edgesFile = sys.argv[3]
nodesFile = sys.argv[4]
resultFile = sys.argv[5]
paymentsFile = sys.argv[6]

processCount = 4
X = [[multiprocessing.Value("f", 0.0, lock=False) for j in range(sampleSize // processCount)] for i in range(processCount)]

def efSampler(G, randS, randT, processId, costCoef=1):
    for i in range(sampleSize // processCount):
        s, t = randS, randT[i]
        mincostFlow = nx.max_flow_min_cost(G, s, t)
        mincost = nx.cost_of_flow(G, mincostFlow)
        mincost /= 1000000
        mincostFlowValue = sum((mincostFlow[u][t] for u in G.predecessors(t))) - sum(
            (mincostFlow[t][v] for v in G.successors(t))
        )
        
        fund = sum((G[s][u]['capacity'] for u in G.successors(s)))
        if fund == 0:
            X[processId][i].value = 0
            continue
        X[processId][i].value = (mincostFlowValue - costCoef * mincost) / fund
        # print(X[processId][i])
    

def writeResultIntoFile(nodeId, nodeEf, nodeEfConf, nodeSuccessRate):
    # node_id, node_ef, node_conf, success_rate
    row = [nodeId, nodeEf, nodeEfConf, nodeSuccessRate]
    with open(resultFile, 'a') as f:
        writer = csv.writer(f)
        writer.writerow(row)

def dataExtractor(G, randS, nodeList, payments):
    efResult = []
    successResult = []
    for k in range(dataSize):
        ## effective flow
        ### multiprocessing
        randT = random.sample(nodeList, sampleSize)
        # print(randT)
        p0 = multiprocessing.Process(target=efSampler, args=(G, randS[k], randT[0:sampleSize // processCount], 0,))
        p1 = multiprocessing.Process(target=efSampler, args=(G, randS[k], randT[sampleSize // processCount: 2 * sampleSize // processCount], 1,))
        p2 = multiprocessing.Process(target=efSampler, args=(G, randS[k], randT[sampleSize // 2: 3 * sampleSize // processCount], 2,))
        p3 = multiprocessing.Process(target=efSampler, args=(G, randS[k], randT[3 * sampleSize // processCount: sampleSize], 3,))

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

        efResult.append((randS[k], np.mean(Xjoined), 2*(np.std(Xjoined) / np.sqrt(sampleSize))))

        successResult.append(successRateCalculator(randS[k], payments))

        writeResultIntoFile(efResult[k][0], efResult[k][1], efResult[k][2], successResult[k])
    # return efResult

def successRateCalculator(randS, payments):
    succeededPayments = payments[(payments['sender_id'] == randS) & (payments['is_success'] == 1)].count()[0]
    totalPayments = payments[(payments['sender_id'] == randS)].count()[0]
    return float(succeededPayments) / totalPayments

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
# G.add_nodes_from(nodeList)

## payments
payments = pd.read_csv(paymentsFile)
paymentsSenders = list(payments['sender_id'])
randS = random.sample(paymentsSenders, dataSize)


dataExtractor(G, randS, nodeList, payments)
## other centralities
### betweenness
# bcResult = []
# bcResult = nx.betweenness_centrality(G, weight=False, normalized=False)