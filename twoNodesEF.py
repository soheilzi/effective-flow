import sys, pandas as pd, networkx as nx, matplotlib.pyplot as plt

def graphConstructor(edgesFile, nodesFile):
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

    return G

def effectiveFlow(G, s, t, costCoef):
    mincostFlow = nx.max_flow_min_cost(G, s, t)
    mincost = nx.cost_of_flow(G, mincostFlow)
    mincost /= 1000000
    mincostFlowValue = sum((mincostFlow[u][t] for u in G.predecessors(t))) - sum(
        (mincostFlow[t][v] for v in G.successors(t))
    )

    fund = sum((G[s][u]['capacity'] for u in G.successors(s)))
    if fund == 0:
        return 0
    return (mincostFlowValue - costCoef * mincost) / fund, fund

def dataExtractor(paymentsDf, source, target):
    receivedAmount = [[] for i in range(len(source))]
    sentAmount = [[] for i in range(len(source))]
    for index, row in paymentsDf.iterrows():
        if (row['sender_id'] in source) and (row['receiver_id'] in target):
            dataIndex = source.index(row['sender_id'])
            receivedAmount[dataIndex].append(0 if row['is_success'] == 0 else row['amount'])
            sentAmount[dataIndex].append(row['amount'])
    
    return receivedAmount, sentAmount

def makeAccumulative(data):
    accumulativeData = [[0 for i in range(len(data[0]))] for j in range(len(data))]
    for i in range(len(data)):
        total = 0
        for j in range(len(data[i])):
            total += data[i][j]
            accumulativeData[i][j] = total

    return accumulativeData

def plotData(s, t, ef, fund, receivedAmount, sentAmount):
    plt.plot(sentAmount, receivedAmount, label='amount')
    plt.plot(sentAmount, [ef * fund] * len(sentAmount), label="ef*fund")
    plt.xlabel("sent amount")
    plt.ylabel("received amount")
    plt.title("s:%d t:%d ef:%f fund:%f"%(s, t, ef, fund))
    plt.show()


paymentsFile = sys.argv[1]
edgesFile = sys.argv[2]
nodesFile = sys.argv[3]
costCoef = int(sys.argv[4])

source = list(map(int, input().split(",")))
target = list(map(int, input().split(",")))

G = graphConstructor(edgesFile, nodesFile)

paymentsDf = pd.read_csv(paymentsFile)
paymentsDf = paymentsDf.sort_values(by=["start_time"], ignore_index=True)
receivedAmount, sentAmount = dataExtractor(paymentsDf, source, target)
accumulativeReceivedAmount = makeAccumulative(receivedAmount)
accumulativeSentAmount = makeAccumulative(sentAmount)

for i in range(len(source)):
    ef, fund = effectiveFlow(G, source[i], target[i], costCoef)
    plotData(source[i], target[i], ef, fund, accumulativeReceivedAmount[i], accumulativeSentAmount[i])