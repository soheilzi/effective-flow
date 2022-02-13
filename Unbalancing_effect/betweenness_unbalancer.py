from matplotlib import lines
import pandas as pd
import sys
import random

from pyparsing import line

def read_centrality_file():
    f = open("sorted_centrality.txt", "r")
    lines = f.readlines()
    f.close()
    return lines

def find_index(channel_id, channels_df):
    return channels_df.index[channels_df['id'] == channel_id].tolist()
    print(channel_id)

def select_most_betweens(channleUnbalancedCount, channels_df):
    indexes = []
    lines = read_centrality_file()
    for line in lines[:channleUnbalancedCount]:
        # print(find_index(int(line), channels_df), int(line))
        indexes.append(find_index(int(line), channels_df)[0])
    return indexes

def select_channels(file, channleUnbalancedCount):
    df = pd.read_csv(file)
    # select_most_betweens(channleUnbalancedCount, df)
##    # args = random.sample(df.index.values.tolist(), channleUnbalancedCount)  
    args = select_most_betweens(channleUnbalancedCount, df)
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