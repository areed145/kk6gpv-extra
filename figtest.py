import os
import numpy as np
import pandas as pd
from pymongo import MongoClient
import plotly
import plotly.graph_objs as go
import json
from datetime import datetime, timedelta

client = MongoClient('mongodb://kk6gpv:kk6gpv@localhost:27017/')
sid = 'KTXHOUST1941'

db = client.wx

df_wx_raw = pd.DataFrame(list(db.raw.find({
    'station_id': sid,
}).limit(100).sort([('observation_time_rfc822', -1)])))
df_wx_raw.index = df_wx_raw['observation_time_rfc822']

for col in df_wx_raw.columns:
    try:
        df_wx_raw.loc[df_wx_raw[col] < -50, col] = pd.np.nan
    except:
        pass

df_wx_raw['cloudbase'] = (
    (df_wx_raw['temp_f'] - df_wx_raw['dewpoint_f']) / 4.4) * 1000 + 50
df_wx_raw.loc[df_wx_raw['pressure_in'] < 0, 'pressure_in'] = pd.np.nan

df_wx_raw['dat'] = df_wx_raw.index
df_wx_raw.sort_values(by='dat', inplace=True)
df_wx_raw['temp_delta'] = df_wx_raw.temp_f.diff()
df_wx_raw['precip_today_delta'] = df_wx_raw.precip_today_in.diff()
df_wx_raw.loc[df_wx_raw['precip_today_delta']
              < 0, 'precip_today_delta'] = 0
df_wx_raw['precip_cum_in'] = df_wx_raw.precip_today_delta.cumsum()
df_wx_raw['pres_delta'] = df_wx_raw.pressure_in.diff()
df_wx_raw['dat_delta'] = df_wx_raw.dat.diff().dt.seconds / 360
df_wx_raw['dTdt'] = df_wx_raw['temp_delta'] / df_wx_raw['dat_delta']
df_wx_raw['dPdt'] = df_wx_raw['pres_delta'] / df_wx_raw['dat_delta']

df_wx_raw['date'] = df_wx_raw.index.date
df_wx_raw['hour'] = df_wx_raw.index.hour

df_wx_raw.loc[df_wx_raw['wind_mph'] == 0, 'wind_cat'] = 'calm'
df_wx_raw.loc[df_wx_raw['wind_mph'] > 0, 'wind_cat'] = '0-1'
df_wx_raw.loc[df_wx_raw['wind_mph'] > 1, 'wind_cat'] = '1-2'
df_wx_raw.loc[df_wx_raw['wind_mph'] > 2, 'wind_cat'] = '2-5'
df_wx_raw.loc[df_wx_raw['wind_mph'] > 5, 'wind_cat'] = '5-10'
df_wx_raw.loc[df_wx_raw['wind_mph'] > 10, 'wind_cat'] = '>10'

df_wx_raw['wind_degrees_cat'] = np.floor(
    df_wx_raw['wind_degrees'] / 15) * 15
df_wx_raw.loc[df_wx_raw['wind_degrees_cat'] == 360, 'wind_degrees_cat'] = 0
df_wx_raw['wind_degrees_cat'] = df_wx_raw['wind_degrees_cat'].fillna(
    0).astype(int).astype(str)

df_wx_raw.loc[df_wx_raw['wind_mph'] == 0, 'wind_degrees'] = pd.np.nan

wind = df_wx_raw[['wind_cat', 'wind_degrees_cat']]
wind['count'] = 1
ct = len(wind)
wind = pd.pivot_table(wind, values='count', index=[
    'wind_degrees_cat'], columns=['wind_cat'], aggfunc=np.sum)
ix = np.arange(0, 360, 5)
col = ['calm', '0-1', '1-2', '2-5', '5-10', '>10']
wind_temp = pd.DataFrame(data=0, index=ix, columns=col)
for i in ix:
    for j in col:
        try:
            wind_temp.loc[i, j] = wind.loc[str(i), j]
        except:
            pass
wind_temp = wind_temp.fillna(0)
wind_temp['calm'] = wind_temp['calm'].mean()
for col in range(len(wind_temp.columns)):
    try:
        wind_temp.iloc[:, col] = wind_temp.iloc[:, col] + \
            wind_temp.iloc[:, col-1]
    except:
        pass
wind_temp = np.round(wind_temp / ct * 100, 2)
wind_temp['wind_cat'] = wind_temp.index

dt_min = df_wx_raw.index.min()
dt_max = df_wx_raw.index.max()

td_max = max(df_wx_raw['temp_f'].max(), df_wx_raw['dewpoint_f'].max()) + 1
td_min = min(df_wx_raw['temp_f'].min(), df_wx_raw['dewpoint_f'].min()) - 1

df_thp = df_wx_raw[['temp_f', 'relative_humidity', 'pressure_in']]
df_thp = df_thp.copy(deep=True)
df_thp.dropna(inplace=True)
df_thp = df_thp.drop_duplicates(
    subset=['temp_f', 'relative_humidity'], keep='first')

print(df_thp['temp_f'].min(), df_thp['temp_f'].max())
print(df_thp['relative_humidity'].min(), df_thp['relative_humidity'].max())
print(df_thp['pressure_in'].min(), df_thp['pressure_in'].max())
print(len(df_thp))

test = pd.pivot_table(df_thp, values='pressure_in', index=['temp_f'], columns=[
                      'relative_humidity'], aggfunc=np.mean)
test.shape


data_thp = [
    go.Surface(x=df_thp['temp_f'],
               y=df_thp['relative_humidity'],
               z=df_thp['pressure_in'],
               colorscale='YlGnBu',
               )
]

layout_thp = go.Layout(autosize=True,
                       scene={'xaxis': {
                           'title': 'Temperature (F)',
                           'tickfont': {'size': 10},
                                    'titlefont': {'color': 'rgb(255, 95, 63)'},
                                    'type': 'linear'
                       },
                           'yaxis': {
                           'title': 'Humidity (%)',
                                    'tickfont': {'size': 10},
                                    'titlefont': {'color': 'rgb(63, 127, 255)'},
                                    'tickangle': 1
                       },
                           'zaxis': {
                           'title': 'Pressure (inHg)',
                                    'tickfont': {'size': 10},
                                    'titlefont': {'color': 'rgb(127, 255, 63)'},
                       },
                           'camera': {'eye': {'x': 2, 'y': 1, 'z': 1.25}},
                           'aspectmode': 'cube', })

fig = go.Figure(data=data_thp, layout=layout_thp)
fig.show()
