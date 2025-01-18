import pandas as pd
import matplotlib.pyplot as plt

print(pd.__version__)

data_path = "resources\\usfs_data.csv"


causes = pd.read_csv(data_path, usecols=['STATCAUSE', 'TOTALACRES'])


# read causes as strings
causes['STATCAUSE'].astype(str)

# cause count graphing
cause_counts = causes['STATCAUSE'].value_counts()
defined_categories = ['Lightning', 'Undetermined', 'Camping', 'Equipment', 'Incendiary', 'Debris/Open Burning', 'Other Human Cause', 'Arson']
usfs_filtered_causes = causes[(causes['STATCAUSE'].isin(defined_categories)) & (causes['TOTALACRES'] > 1000)]

all_other_causes = usfs_filtered_causes['STATCAUSE'].apply(
    lambda x: x if x in defined_categories else 'Other'
)

aoc_counts = all_other_causes.value_counts()

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

plt.savefig('results-gen\\causecount.pdf')