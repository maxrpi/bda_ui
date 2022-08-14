import requests
import json

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

  print(url, username, role, password)
  response = perform_graphql_request(f"""
    mutation authRequest {{
      authenticationRequest(
        input: {{authenticator: "{username}", role: "{role}", userName: "{username}"}}
      ) {{
        jwtRequest {{
          challenge, message
        }}
      }}
    }}
  """, url = url) 
  jwt_request = response['data']['authenticationRequest']['jwtRequest']
  if jwt_request['challenge'] is None:
    raise AuthenticationError(jwt_request['message'])
  else:
      print("Challenge received: " + jwt_request['challenge'])
      response=perform_graphql_request(f"""
        mutation authValidation {{
          authenticationValidation(
            input: {{authenticator: "{username}", signedChallenge: "{jwt_request["challenge"]}|{password}"}}
            ) {{
            jwtClaim
          }}
        }}
    """, url = url)

  try:
    jwt_claim = response['data']['authenticationValidation']['jwtClaim']
  except KeyError as err:
    raise AuthenticationError('Error getting JWT. Platform responded {}'.format(response))

  return jwt_claim

def get_equipment_description(url, token, eq_id):

  print("Requesting Data from CESMII Smart Manufacturing Platform...")
  print()

  ''' Request some timeseries data''' 
  smp_query = f'''
      query eqById {{
        equipment(id: "{eq_id}") {{
          displayName
          attributes {{
            datatype
            id
          }}
        }}
      }}'''


  attribute_name = "Electric Potential"
  equipment_name = "Motor"
  smp_query = f'''
        query {{
                    typeToAttributeTypes(filter: {{displayName: {{equalTo: "{attribute_name}"}}}}) {{
                        id
                        dataType
                        maxValue
                        id
                        displayName
                        partOf {{
                        description
                        id
                            thingsByTypeId(filter:  {{displayName: {{equalTo: "{equipment_name}"}}}}) {{
                                displayName
                                id
                                updatedTimestamp
                                attributesByPartOfId(filter: {{displayName: {{equalTo: "{attribute_name}"}}}}) {{
                                    floatValue
                                    intValue
                                    id
                                }}
                            }}
                        }}
                    }}
            }}
    '''

  smp_query = f'''
    query attribById {{
      attribute(id: "{eq_id}") {{
        id
        dataType
        description
        displayName
        updatedTimestamp
        createdTimestamp
        datetimeValue
        objectValue
        }}
      }} 
  '''
  print(smp_query)
  try:
    smp_response = perform_graphql_request(smp_query, url,  headers={"Authorization": f"Bearer {token}"})
    print("SMP_RESPONSE={}".format(smp_response))
    return smp_response['data']
  except Exception as err:
    if "forbidden" in str(err).lower() or "unauthorized" in str(err).lower():
      raise(AuthenticationError(err))
    else:
      raise(err)