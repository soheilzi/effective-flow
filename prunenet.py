import pandas as pd
import sys
import random

def remove_row_channels(file, channelsDelNum):
    df = pd.read_csv(file)
    args = random.sample(df.index.values.tolist(), channelsDelNum)  
    deletedRows = df.iloc[args]
    df = df.drop(index=args)
    # df.to_csv(file, index=False)
    return deletedRows['id'], df

def remove_specific_row_from_csv(file, column_name, args):
    df = pd.read_csv(file)
    for row in args:
        df = df[eval("df.{}".format(column_name)) != row]
    # df.to_csv(file, index=False)
    return df


channelsDelNum = int(sys.argv[1])
channelsFile = sys.argv[2]
edgesFile = sys.argv[3]

deletedRows, channelsDf = remove_row_channels(channelsFile, channelsDelNum)
edgesDf = remove_specific_row_from_csv(edgesFile, "channel_id", deletedRows)

## postprocessing
channelsDf.to_csv("test1.csv", index=False)

for index, row in channelsDf.iterrows():
    channelsDf['id'] = channelsDf['id'].replace([row['id']], index)
    edgesDf['channel_id'] = edgesDf['channel_id'].replace([row['id']], index)
    

channelsDf.to_csv("test2.csv", index=False)

# for index, row in edgesDf.iterrows():
#     edgesDf['id'] = edgesDf['id'].replace([row['id']], index)
#     channelsDf['edge1_id'] = channelsDf['edge1_id'].replace([row['id']], index)
#     channelsDf['edge2_id'] = channelsDf['edge2_id'].replace([row['id']], index)

# channelsDf.to_csv(channelsFile, index=False)
# edgesDf.to_csv(edgesFile, index=False)