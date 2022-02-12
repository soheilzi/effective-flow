import pandas as pd
import sys
import random

df = pd.read_csv('../cloth/channels_ln.csv')
print(len(df.index.values.tolist()))