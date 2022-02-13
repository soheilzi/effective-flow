import pandas as pd
import sys
import random

def select_most_between(channels_df, channleUnbalancedCount):
    pass#returns args

def select_channels(file, channleUnbalancedCount):
    df = pd.read_csv(file)
    args = random.sample(df.index.values.tolist(), channleUnbalancedCount)  
    unbalancedRows = df.iloc[args]
    return unbalancedRows['id'], df

def make_unbalanced_csv(file, args):
    df = pd.read_csv(file)
    
    for row in args:
        onePairEdgesdf = df.loc[df['channel_id'] == row]
        node0 = onePairEdgesdf.iloc[0]['from_node_id']
        node1 = onePairEdgesdf.iloc[0]['to_node_id']
        # print(node0)
        # print(node1)
        newArgs = df.loc[(df['from_node_id'] == node0) & (df['to_node_id'] == node1)]
        newArgs = newArgs['channel_id']
        for newRow in newArgs:
            twoEdgesdf =  df.loc[df['channel_id'] == newRow]
            # print(twoEdgesdf)
            totalBalance = sum(twoEdgesdf['balance'].tolist())
            if twoEdgesdf.iloc[0]['id'] > twoEdgesdf.iloc[1]['id']:
                df.loc[df['id'] == twoEdgesdf.iloc[0]['id'], 'balance'] = totalBalance
                df.loc[df['id'] == twoEdgesdf.iloc[1]['id'], 'balance'] = 0
            else:
                df.loc[df['id'] == twoEdgesdf.iloc[0]['id'], 'balance'] = 0
                df.loc[df['id'] == twoEdgesdf.iloc[1]['id'], 'balance'] = totalBalance
            twoEdgesdf =  df.loc[df['channel_id'] == newRow]
            # print(twoEdgesdf)
    # print(df)        
    return df


channleUnbalancedCount = int(sys.argv[1])
channelsFile = sys.argv[2]
edgesFile = sys.argv[3]

unbalancedRows, channelsDf = select_channels(channelsFile, channleUnbalancedCount)
edgesDf = make_unbalanced_csv(edgesFile, unbalancedRows)

## postprocessing
# channelsDF_copy = channelsDf.copy()
# edgesDF_copy = edgesDf.copy()


edgesDf.to_csv("../cloth/edges_ub.csv", index=False)