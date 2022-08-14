from re import A
import pandas as pd
import numpy as np

def format_time_series_stamped(datafile, index):
  df = pd.read_csv(datafile, usecols=[0,index], parse_dates=[0],
    names=['ts','data'],header=0)  
  start_time = df['ts'].min().strftime("%Y-%m-%dT%H:%M:%SZ")
  end_time = df['ts'].max().strftime("%Y-%m-%dT%H:%M:%SZ")

  stamped_data = ""
  for _, row in df.iterrows(): 
    ts = row['ts'].strftime("%Y-%m-%dT%H:%M:%SZ")
    line = ' {{timestamp: "{}", value: "{}", status: "0" }}\n'.format(ts, row['data'])
    stamped_data = stamped_data + line
  print (start_time, end_time, stamped_data)
  return (start_time, end_time, stamped_data)