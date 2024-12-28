import pandas as pd
import matplotlib.pyplot as plt

print(pd.__version__)

data_path = "usfs_data.csv"


usfs_class = pd.read_csv(data_path, usecols=['SIZECLASS'])


# read acres as floats
usfs_class['SIZECLASS'].astype(str)



# cause count graphing
classcounts = usfs_class['SIZECLASS'].value_counts()
defined_categories = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
filtered_counts = usfs_class[usfs_class['SIZECLASS'].isin(defined_categories)].value_counts()

filter2 = usfs_class['SIZECLASS'].apply(
    lambda x: x if x in defined_categories else 'Not Classified'
)

final_counts = filter2.value_counts()

plt.figure(figsize=(10, 6))
final_counts.plot(kind='bar', color='skyblue', edgecolor='black')

# Add labels and title
plt.title('USFS Classified Fire Counts', fontsize=16)
plt.xlabel('Class', fontsize=12)
plt.ylabel('Number of Occurrences', fontsize=12)
plt.xticks(rotation=45, ha='right')

# Display the plot
plt.tight_layout()
plt.show()

plt.savefig('usfs_plot.png')
