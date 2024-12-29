import pandas as pd
import matplotlib.pyplot as plt

print(pd.__version__)


data_path = "resources\\usfs_data.csv"


acres_burned = pd.read_csv(data_path, usecols=['TOTALACRES'])
year = pd.read_csv(data_path, usecols=['FIREYEAR'])

both = pd.read_csv(data_path, usecols=['TOTALACRES', 'FIREYEAR'])

filtered = both[(both['FIREYEAR'] >= 1900) & (both['FIREYEAR'] <= 2024) & (both['FIREYEAR'] != 0) & (both['FIREYEAR'] != 9999)]
filtered = filtered.dropna(subset=['FIREYEAR', 'TOTALACRES'])
filtered['FIREYEAR'] = filtered['FIREYEAR'].astype(int)

# read acres as floats
filtered['TOTALACRES'].astype(float)

#sum 
acres_per_year = filtered.groupby('FIREYEAR')['TOTALACRES'].sum().sort_index()
cumulative_acres = acres_per_year.cumsum()


# Plot the cumulative acres burned
plt.figure(figsize=(12, 6))
plt.plot(cumulative_acres.index, cumulative_acres.values, marker='o', linestyle='-', color='tab:green')
plt.title('Cumulative Acres Burned Per Year', fontsize=16)
plt.xlabel('Year', fontsize=14)
plt.ylabel('Cumulative Acres Burned', fontsize=14)
plt.xticks(rotation=45)
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()

plt.savefig('results-gen\\cab.pdf')
