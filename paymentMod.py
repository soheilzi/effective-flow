import sys
import random
import pandas as pd

pairsCount = int(sys.argv[1])
paymentsCount = int(sys.argv[2])
paymentsAmount = int(sys.argv[3])
paymentsFile = sys.argv[4]
nodesFile = sys.argv[5]
seed = int(sys.argv[6])


nodeData = pd.read_csv(nodesFile)
nodeList = list(nodeData['id'])

payments = pd.read_csv(paymentsFile)
maxStartTime = max(payments['start_time'])
interval = maxStartTime // paymentsCount

random.seed(seed)
randS = random.sample(nodeList, pairsCount)
randT = random.sample(nodeList, pairsCount)

# print(randS)
# print(randT)
while(len(list(set(randS) & set(randT))) != 0):
    randS = random.sample(nodeList, pairsCount)
    randT = random.sample(nodeList, pairsCount)
payments = payments.drop(payments[(payments['sender_id'].isin(randS)) | (payments['receiver_id'].isin(randS))].index)

t = 1
while(t < maxStartTime + len(randS)):
    for i in range(len(randS)):
        payments = payments.append({"id": 0, "sender_id": randS[i], "receiver_id": randT[i], "amount": paymentsAmount, "start_time": t + i}, ignore_index=True)
    t += interval

payments = payments.sort_values(by=["start_time"], ignore_index=True)
payments.reset_index()
payments["id"] = payments.index

payments.to_csv(paymentsFile, index=False)

print(",".join([str(item) for item in randS]))
print(",".join([str(item) for item in randT]))