import pandas as pd

def remove_specific_row_from_csv(file, args):
    df = pd.read_csv(file)
    df = df.drop(index=args)
    df.to_csv(file, index=False)

