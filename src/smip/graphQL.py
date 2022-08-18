import requests
import json
import pandas as pd
import smip.queries as queries
from support_functions import formatters
from support_functions.formatters import format_time_series_stamped, json_timeseries_to_table

class No_Request(Exception):
  def __init__(self, http_status_code, reason):
    self.http_status_code = http_status_code
    self.reason = reason

class AuthenticationError(Exception):
    def __init__(self, message):
        self.message = message

def perform_graphql_mutation(content, url, headers=None):

  try:
    r = requests.post(url=url, headers=headers, data={"query": content})
  except requests.RequestException as err:
    raise No_Request(-1,err)
  r.raise_for_status()
  if r.ok:
    return r.json()
  else:
    raise No_Request(r.status_code, r.reason)

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
    smp_response = perform_graphql_mutation(query,
      url,
      headers={"Authorization": f"Bearer {token}"}
    )
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
  
  print("get_timeseries_query:\n", query)
  try:
    smp_response = perform_graphql_request(query, url,  headers={"Authorization": f"Bearer {token}"})
  except Exception as err:
    print("get_time_series error:", err)
    if "forbidden" in str(err).lower() or "unauthorized" in str(err).lower():
      raise(AuthenticationError(err))
    else:
      raise(err)
    print(smp_response)
  
  dataframe = json_timeseries_to_table(smp_response['data']['getRawHistoryDataWithSampling'])
  dataframe.rename(columns={"floatvalue": "{}".format(attrib_id)}, inplace=True)
  return dataframe

def get_first_timestamp( url, token, attrib_id):
  query_template = queries.get_first_timestamp
  query = query_template.format(attrib_id=attrib_id)
  try:
    smp_response = perform_graphql_request(query, url,  headers={"Authorization": f"Bearer {token}"})
  except Exception as err:
    if "forbidden" in str(err).lower() or "unauthorized" in str(err).lower():
      raise(AuthenticationError(err))
    else:
      raise(err)

  print(smp_response)
  
  return smp_response['data']