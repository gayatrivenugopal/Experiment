import pandas as pd

class Data:
    def __init__(self):
        self.data = pd.read_csv('RankedWords excl numbers.csv')
        for index, row in self.data.iterrows():
            if self.data.loc[index]['complexity'] >= 3:
                self.data.at[index,'complexity'] = 1
            else:
                self.data.at[index,'complexity'] = 0
        self.data.drop_duplicates(keep = 'first', inplace = True)
