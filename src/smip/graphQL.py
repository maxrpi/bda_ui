import requests
import json
import smip.queries as queries
from support_functions.formatters import format_time_series_stamped

class No_Request(Exception):
  def __init__(self, http_status_code, reason):
    self.http_status_code = http_status_code
    self.reason = reason

class AuthenticationError(Exception):
    def __init__(self, message):
        self.message = message

def perform_graphql_mutation(content, url, headers=None):
  print(content)
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

  print(url, username, role, password)
  query = queries.bearer_token.format(username=username, role=role)
  print("sending query:", query)
  response = perform_graphql_request(query, url=url)

  jwt_request = response['data']['authenticationRequest']['jwtRequest']
  if jwt_request['challenge'] is None:
    raise AuthenticationError(jwt_request['message'])
  else:
      print("Challenge received: " + jwt_request['challenge'])
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
  print("sending query:", query)
  
  try:
    smp_response = perform_graphql_mutation(query,
      url,
      headers={"Authorization": f"Bearer {token}"}
    )
    print("SMP_RESPONSE={}".format(smp_response))
    return smp_response['data']
  except Exception as err:
    if "forbidden" in str(err).lower() or "unauthorized" in str(err).lower():
      raise(AuthenticationError(err))
    else:
      raise(err)

def post_timeseries_id(url, token, attrib_id, filename):
  print("calling post_timeseries_id with {}",[url, token,attrib_id, filename])
  (start_time, end_time, stamped_data) = format_time_series_stamped(filename, index=1)
  print("getting query template")
  query = queries.update_timeseries
  print("query template: \n", query)
  try:
    query = query.format(attrib_id=attrib_id,
      start_time=start_time, end_time=end_time, stamped_data=stamped_data)
  except Exception as err:
    print(err)
  
  print("formated query = ",query)
  try:
    smp_response = perform_graphql_request(query, url,  headers={"Authorization": f"Bearer {token}"})
    print("SMP_RESPONSE={}".format(smp_response))
    return smp_response['data']
  except Exception as err:
    if "forbidden" in str(err).lower() or "unauthorized" in str(err).lower():
      raise(AuthenticationError(err))
    else:
      raise(err)