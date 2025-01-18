import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import folium
from folium.plugins import HeatMap
from shapely.geometry import Point
import geopandas as gpd
import openmeteo_requests
import requests_cache
import xgboost as xgb
import pandas as pd
import pandas as pd
from retry_requests import retry
import time
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression
from plotnine import ggplot, aes, geom_point, geom_line, geom_path, labs, annotate, scale_x_continuous, xlim
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split


print(pd.__version__)

data_path_cal = "resources\\california_100acre_fire_weather_data.csv"
data_path_USFS = "resources\\usfs_data.csv"

# Load the California fire weather data
calif = pd.read_csv(data_path_cal, usecols=['date', 'temperature_2m_max', 'temperature_2m_min', 'sunshine_duration', 'precipitation_sum', 'wind_speed_10m_max', 'wind_gusts_10m_max', 'latitude', 'longitude']).dropna()
# Load the USFS data to get the TOTALACRES column
usfs_data = pd.read_csv(data_path_USFS, usecols=['TOTALACRES', 'LATDD83', 'LONGDD83']).dropna()
# Merge the two dataframes on latitude and longitude
calif = calif.merge(usfs_data, left_on=['latitude', 'longitude'], right_on=['LATDD83', 'LONGDD83'], how='left')
# Drop the extra columns from the merge
calif = calif.drop(columns=['LATDD83', 'LONGDD83'])
# Convert sunshine_duration from seconds to hours
calif['sunshine_duration_hours'] = calif['sunshine_duration'] / 3600
# temperature range
calif['temprange'] = calif['temperature_2m_max'] - calif['temperature_2m_min']
# Filter for fires over 100 acres burned
calif = calif[calif['TOTALACRES'] > 100]
calif = calif[calif['TOTALACRES'] < 50000]
# Calculate the average temperature
calif['avg_temperature'] = (calif['temperature_2m_max'] + calif['temperature_2m_min']) / 2
# Log transform the total acres burned to reduce skewness
calif['log_total_acres'] = np.log(calif['TOTALACRES'])  # Add 1 to avoid log(0)
calif['temp_max_bin'] = pd.cut(calif['temperature_2m_max'], bins=5)
calif['temp_min_bin'] = pd.cut(calif['temperature_2m_min'], bins=5)


X = calif[['temperature_2m_max', 'temperature_2m_min', 'sunshine_duration', 'precipitation_sum', 'wind_speed_10m_max', 'wind_gusts_10m_max', 'latitude', 'longitude']]
y = calif['TOTALACRES']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


train_dmatrix = xgb.DMatrix(data=X_train, label=y_train)
test_dmatrix = xgb.DMatrix(data=X_test, label=y_test)
params = {
    'objective': 'reg:squarederror',  # For regression
    'max_depth': 6,
    'eta': 0.3,  # Learning rate
    'subsample': 0.5,
    'colsample_bytree': 0.8,
    'seed': 42,
    'objective': 'reg:squarederror'
}

model = xgb.train(params, train_dmatrix, num_boost_round=100)

y_pred = model.predict(test_dmatrix)

#performance evaluation
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f'MSE: {mse}, R²: {r2}')

# Perform cross-validation
xgb_cv = xgb.cv(params, train_dmatrix, num_boost_round=100, nfold=5, metrics={'rmse'}, seed=42)

# Plot feature importance
fig, ax = plt.subplots(figsize=(10, 8))
xgb.plot_importance(model, ax=ax, importance_type='weight')
plt.show()