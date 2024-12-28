import pandas as pd
import matplotlib.pyplot as plt

print(pd.__version__)

data_path = "usfs_data.csv"


acres_burned = pd.read_csv(data_path, usecols=['TOTALACRES'])


# read acres as floats
acres_burned['TOTALACRES'].astype(float)


# create bins
bins = [0, 0.5, 1, 5, 10, 20, 30, 40, 50, 60, 70, 80, 100,]


plt.figure(figsize=(10, 6))
aoc_counts.plot(kind='bar', color='skyblue', edgecolor='black')

# Add labels and title
plt.title('USFS Wildland Fire Causes', fontsize=16)
plt.xlabel('Cause', fontsize=12)
plt.ylabel('Number of Occurrences', fontsize=12)
plt.xticks(rotation=45, ha='right')

# Display the plot
plt.tight_layout()
plt.show()

plt.savefig('causes_plot.png')