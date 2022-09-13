import json
import pandas as pd
import dateutil.parser
import numpy as np
from datetime import datetime

timeformat = "%Y-%m-%dT%H:%M:%SZ"

def max_time_range(as_datetime=False):
    start_time = dateutil.parser.parse("1900-01-01")
    end_time = dateutil.parser.parse("2200-01-01")
    if as_datetime:
      return (start_time, end_time)
    return (start_time.strftime(timeformat), end_time.strftime(timeformat))

def format_time_series_stamped(datafile, index, max_timerange=False):
  df = pd.read_csv(datafile, usecols=[0,index], parse_dates=[0], dayfirst=True,
    names=['ts','data'],header=0)  
  if not max_timerange:
    start_time = df['ts'].min().strftime("%Y-%m-%dT%H:%M:%SZ")
    end_time = df['ts'].max().strftime("%Y-%m-%dT%H:%M:%SZ")
  else:
    (start_time, end_time) = max_time_range()

  stamped_data = ""
  for _, row in df.iterrows(): 
    ts = row['ts'].strftime("%Y-%m-%dT%H:%M:%SZ")
    line = ' {{timestamp: "{}", value: "{}", status: "0" }}\n'.format(ts, row['data'])
    stamped_data = stamped_data + line
  return (start_time, end_time, stamped_data)

def standardize_timestamp(timestamp, unix_timestamp=False):
  if unix_timestamp:
    as_datetime = datetime.fromtimestamp(timestamp)
  else: 
    as_datetime = timestamp
  return as_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")

def table_to_lotseries(timestamp_start, ts_increment, table, unix_timestamp=False):
  entries = []
  time = timestamp_start
  for row in table:
    entries.append(row_to_lot(time, row, unix_timestamp))
    time = time + ts_increment
  return "\n".join(entries)


def row_to_lot(timestamp, row, unix_timestamp):
  timestamp_str = standardize_timestamp(timestamp, unix_timestamp)
  id = row[0]
  array = ",".join([str(item) for item in row[1:]])
  array_string = '"{{\\"id\\": \\"{}\\", \\"data\\": \\"[{}]\\"}}"'.format(id, array)
  return f'''{{timestamp: \"{timestamp_str}\", status: \"0\", value: {array_string} }}'''


def json_timeseries_to_table(jd):
  
  df = pd.DataFrame.from_dict(jd)
  df['ts'] = pd.to_datetime(df['ts'], dayfirst=True)
  return df

def break_df_into_ranges(df: pd.DataFrame):
  df.sort_index(inplace=True)
  missing_rows = np.array(df.isnull()).any(axis=1)

  N = len(missing_rows)
  missing_rows = np.concatenate([missing_rows,np.array([True])])
  ll = N
  ul = 0
  good_ranges = []
  for i, missing in enumerate(missing_rows):
    if not missing:
      ul = i
      if ll == N:
        ll = i
      continue
    if missing and ll < N:
      good_ranges.append((ll, ul))
      ll = N

  df_list = []
  for (ll, ul) in good_ranges:
    df_list.append(df.iloc[ll:ul+1])
  return df_list
      

def combine_dataframes(df_list, period):

  N = len(df_list)
  times = []
  signs = []
  frame_ids = []
  for index, df in enumerate(df_list):
    range_bins = break_df_into_ranges(df)
    ti = list(df.columns).index('ts')
    starts = []
    stops = []
    starts = [bin.iloc[0,ti] for bin in range_bins]
    stops = [bin.iloc[-1,ti] for bin in range_bins]
    times_t = starts + stops
    times = times + times_t
    signs = signs + [1] * len(starts) + [-1] * len(stops)
    frame_ids = frame_ids + [index] * len(times)

  times = np.array(times)
  signs = np.array(signs)
  frame_ids = np.array(frame_ids)

  sort_index = times.argsort()
  times = times[sort_index]
  signs = signs[sort_index]
  frame_ids = frame_ids[sort_index]

  level = 0
  stopping = False
  range_starts = []
  range_stops = []
  for t, s, f in zip(times, signs, frame_ids):
    if stopping:
      range_stops.append(t)
      stopping = False
    level = level + s
    if level == N:
      range_starts.append(t)
      stopping = True

  assert(len(range_starts) == len(range_stops))
  nrange_starts = np.array(range_starts)

  def to_float(d, epoch=nrange_starts[0]):
    return (d - epoch).total_seconds()

  for (start_time, end_time) in zip(range_starts, range_stops):
    n_points = int((end_time - start_time) / period)
    timegrid = list(pd.date_range(start_time, end_time, n_points))
    if 'interpolation_ts_list' not in locals():
      interpolation_ts_list = timegrid
    else: 
      interpolation_ts_list = interpolation_ts_list + timegrid
  
  tab={'ts': interpolation_ts_list}
  for j, df in enumerate(df_list):
    label = df.columns[1]
    x = df.iloc[:,0]
    y = df.iloc[:,1].values
    itl_n = np.array([to_float(t) for t in interpolation_ts_list])
    x_n = np.array([to_float(t) for t in x])
    ft = np.interp(itl_n, x_n, y)
    tab[label] = ft

  return pd.DataFrame.from_dict(tab)
    



