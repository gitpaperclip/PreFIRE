import pandas as pd
import matplotlib.pyplot as plt

print(pd.__version__)

data_path = "usfs_data.csv"


year = pd.read_csv(data_path, usecols=['FIREYEAR'])
#filter to avoid random corrupted years that throw off data summary
filteryear = year[(year['FIREYEAR'] >= 1900.00) & (year['FIREYEAR'] <= 2024.00)]
filteryear = filteryear.dropna(subset=['FIREYEAR'])

# read each data as CORRECT File type to ensure plot appears correctly
filteryear['FIREYEAR'].astype(int)

filteryear['YEAR_INT_FILTER'] = (filteryear['FIREYEAR'] // 1) * 1

totalcounts = filteryear['YEAR_INT_FILTER'].value_counts().sort_index()

rolling_avg = totalcounts.rolling(window=5).mean()

# Plot the counts of fires per year with a rolling average
plt.figure(figsize=(12, 6))
plt.plot(totalcounts.index, totalcounts.values, marker='o', linestyle='-', color='tab:blue', label='Fire Frequency')
plt.plot(rolling_avg.index, rolling_avg.values, linestyle='--', color='tab:red', label='5-Year Rolling Average')

# Customize the plot
plt.title('Wildfire Frequency Over Time', fontsize=16)
plt.xlabel('Year', fontsize=14)
plt.ylabel('Number of Fires', fontsize=14)
plt.xticks(rotation=45)  # Rotate x-axis labels for readability
plt.grid(True, linestyle='--', alpha=0.6)  # Gridlines for clarity
plt.tight_layout()  # Ensure the plot fits nicely in the figure

# Add a legend to differentiate between the lines
plt.legend()

# Show the plot
plt.show()