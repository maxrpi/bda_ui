import requests
import json
import numpy as np
import pandas as pd
import smip.queries as queries
from support_functions import formatters
from support_functions.formatters import format_time_series_stamped,\
    json_timeseries_to_table, max_time_range, table_to_lotseries
from datetime import datetime, timedelta

class No_Request(Exception):
  def __init__(self, http_status_code, reason):
    self.http_status_code = http_status_code
    self.reason = reason

class AuthenticationError(Exception):
    def __init__(self, message):
        self.message = message

def perform_graphql_request(content, url, headers=None):
  try:
    r = requests.post(url=url, headers=headers, data={"query": content})
  except requests.RequestException as err:
    raise No_Request(-1,err)
  r.raise_for_status()
  if r.ok:
    return r.json()
  else:
    raise No_Request(r.status_code, r.reason)

def get_bearer_token (url, username, role, password):

  query = queries.bearer_token.format(username=username, role=role)
  response = perform_graphql_request(query, url=url)

  jwt_request = response['data']['authenticationRequest']['jwtRequest']
  if jwt_request['challenge'] is None:
    raise AuthenticationError(jwt_request['message'])
  else:
      query = queries.challenge_response.format(username=username,
        challenge=jwt_request['challenge'],
        password=password)
      response=perform_graphql_request(query, url=url)

  try:
    jwt_claim = response['data']['authenticationValidation']['jwtClaim']
  except KeyError as err:
    raise AuthenticationError('Error getting JWT. Platform responded {}'.format(response))

  return jwt_claim

def get_equipment_description(url, token, attrib_id):

  query = queries.attrib_by_id.format(attrib_id=attrib_id)
  
  try:
    smp_response = perform_graphql_request(query,
      url,
      headers={"Authorization": f"Bearer {token}"}
    )
    return smp_response['data']
  except Exception as err:
    if "forbidden" in str(err).lower() or "unauthorized" in str(err).lower():
      raise(AuthenticationError(err))
    else:
      raise(err)


def post_lot_series_id(url, token, attrib_id, filename, delete_all=False, replace_all=False):
  table = pd.read_csv(filename, header=0).to_numpy()
  (start_time, end_time) = max_time_range()
  time_incr = timedelta(seconds=60)
  (first_time_index, _) = max_time_range(as_datetime=True)
  first_time_index =  first_time_index + time_incr
  query_template = queries.update_lot_series
  entries = table_to_lotseries(first_time_index, time_incr, table, unix_timestamp=False)
  query = query_template.format(attrib_id=attrib_id,
    start_time=start_time, end_time=end_time, entries=entries)
  
  try:
    smp_response = perform_graphql_request(query, url,  headers={"Authorization": f"Bearer {token}"})
    return smp_response['data']
  except Exception as err:
    if "forbidden" in str(err).lower() or "unauthorized" in str(err).lower():
      raise(AuthenticationError(err))
    else:
      raise(err)

def post_timeseries_id(url, token, attrib_id, filename, delete_all=False, replace_all=False):
  (start_time, end_time, stamped_data) = \
    format_time_series_stamped(filename, index=1, max_timerange=replace_all)
  query_template = queries.update_timeseries
  query = query_template.format(attrib_id=attrib_id,
    start_time=start_time, end_time=end_time, stamped_data=stamped_data)
  
  try:
    smp_response = perform_graphql_request(query, url,  headers={"Authorization": f"Bearer {token}"})
    return smp_response['data']
  except Exception as err:
    if "forbidden" in str(err).lower() or "unauthorized" in str(err).lower():
      raise(AuthenticationError(err))
    else:
      raise(err)


def delete_timeseries_id(url, token, attrib_id):
  (start_time, end_time) = formatters.max_time_range()
  query_template = queries.update_timeseries
  query = query_template.format(attrib_id=attrib_id,
    start_time=start_time, end_time=end_time, stamped_data="")
  try:
    smp_response = perform_graphql_request(query, url,  headers={"Authorization": f"Bearer {token}"})
    return smp_response['data']
  except Exception as err:
    if "forbidden" in str(err).lower() or "unauthorized" in str(err).lower():
      raise(AuthenticationError(err))
    else:
      raise(err)

def get_timeseries_array(url, token, attrib_id_list,
  start_time, end_time, max_samples, period) -> pd.DataFrame:
  dataframes = []
  for attrib_id in attrib_id_list:
    dataframes.append(get_timeseries(url, token, attrib_id, start_time, end_time, max_samples))
  
  return formatters.combine_dataframes(dataframes, period)

def get_timeseries(url, token, attrib_id, start_time, end_time, max_samples):

  query_template = queries.get_timeseries
  query = query_template.format(index=1, attrib_id=attrib_id,
    start_time=start_time, end_time=end_time, max_samples=max_samples)
  
  try:
    smp_response = perform_graphql_request(query, url,  headers={"Authorization": f"Bearer {token}"})
  except Exception as err:
    if "forbidden" in str(err).lower() or "unauthorized" in str(err).lower():
      raise(AuthenticationError(err))
    else:
      raise(err)
    print(smp_response)
  
  dataframe = json_timeseries_to_table(smp_response['data']['getRawHistoryDataWithSampling'])
  dataframe.rename(columns={"floatvalue": "{}".format(attrib_id)}, inplace=True)
  return dataframe

def get_lot_series(url, token, attrib_id):

  (start_time, end_time) = max_time_range()
  query_template = queries.get_lot_series
  query = query_template.format(index=1, attrib_id=attrib_id, start_time=start_time, end_time=end_time)
  
  try:
    smp_response = perform_graphql_request(query, url,  headers={"Authorization": f"Bearer {token}"})
  except Exception as err:
    if "forbidden" in str(err).lower() or "unauthorized" in str(err).lower():
      raise(AuthenticationError(err))
    else:
      raise(err)
  
  table = smp_response['data']['attribute']['getTimeSeries']
  ids = []
  arrays = []
  for row in table:
    data = json.loads(row["objectvalue"])
    ids.append(int(float(data["id"])))
    array_string = data["data"].replace("[","").replace("]","")
    array = (np.fromstring(array_string, sep=","))
    arrays.append(array)
  
  df = pd.DataFrame(arrays)
  df["id"] = ids
  df.astype({'id': 'int32'}).dtypes
  cols = df.columns.tolist()
  cols = cols[-1:] + cols[:-1]
  df = df[cols]
  df.set_index("id")
  return df

def get_raw_attribute_data( url, token, attrib_id, as_timestamp=True, strip_nan=False):
  query_template = queries.get_raw_attribute_data
  (start_time, end_time) = max_time_range()
  query = query_template.format(attrib_id=attrib_id, start_time=start_time, end_time=end_time)
  try:
    smp_response = perform_graphql_request(query, url, headers={"Authorization": f"Bearer {token}"})
  except Exception as err:
    if "forbidden" in str(err).lower() or "unauthorized" in str(err).lower():
      raise(AuthenticationError(err))
    else:
      raise(err)

  df = pd.DataFrame.from_dict(smp_response['data']['attribute']['getTimeSeries'])
  if strip_nan:
    df.dropna(inplace=True)
  if as_timestamp:
    df['ts'] = pd.to_datetime(df.ts)
    df['ts'] = df.ts.astype('int64') //  10**9
  return df.to_csv(index=False)