import pandas as pd
from src.aadt_calculator import AADTCalculator

# load data
df = pd.read_csv("data/input/i5-cmcp-2019-sec1.csv")

# load AADT Calculator
calculator = AADTCalculator(df)

result_df = calculator.calculate_segment_aadt()
print(result_df)

result_dict = calculator.calculate_group_average_aadt(direction="N", type="ML")
# print(result_dict)

summary_df = calculator.calculate_all_groups()
print(summary_df)

summary_dict = calculator.get_summary_stats()
print(summary_dict)
