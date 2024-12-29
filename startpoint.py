import pandas as pd
import matplotlib.pyplot as plt

print(pd.__version__)

data_path = "usfs_data.csv"


location_data_lat_long = pd.read_csv(data_path, usecols=['LATDD83', 'LONGDD83'])
causes = pd.read_csv(data_path, usecols=['STATCAUSE'])
acres_burned = pd.read_csv(data_path, usecols=['TOTALACRES'])
year = pd.read_csv(data_path, usecols=['FIREYEAR'])
usfs_class = pd.read_csv(data_path, usecols=['SIZECLASS'])


# read each data as CORRECT File type to ensure plot appears correctly
causes['STATCAUSE'].astype(str)