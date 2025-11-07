"""Quick tests to understand utils.py and data_loader.py"""

import pandas as pd
from src import utils
from src.data_loader import DataLoader

# test 1: load data
loader = DataLoader()
df = loader.load_section_data(2019, 1)

# print(df.head(5))

# test 2: calculate aadt for the first row
total_aadt, auto_aadt, truck_aadt = utils.calculate_aadt(df.iloc[0:1])
print(auto_aadt)
