import pandas as pd
import sys
import random

def remove_row_channels(file, channelsDelNum):
    df = pd.read_csv(file)
    args = random.sample(df.index.values.tolist(), channelsDelNum)
    deletedRows = df.iloc[args]
    df = df.drop(index=args)
    df.to_csv(file, index=False)
    return deletedRows['id']

def remove_specific_row_from_csv(file, column_name, args):
    df = pd.read_csv(file)
    for row in args:
        df = df[eval("df.{}".format(column_name)) != row]
    df.to_csv(file, index=False)


channelsDelNum = int(sys.argv[1])
channelsFile = sys.argv[2]
edgesFile = sys.argv[3]

remove_specific_row_from_csv(edgesFile, "channel_id", remove_row_channels(channelsFile, channelsDelNum))