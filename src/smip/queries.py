
bearer_token = '''
  mutation authRequest {{
    authenticationRequest(
      input: {{authenticator: "{username}", role: "{role}", userName: "{username}"}})
      {{
        jwtRequest {{
          challenge, message
      }}
    }}
  }}
  '''

challenge_response = '''
  mutation authValidation {{
    authenticationValidation(
      input: {{authenticator: "{username}",
      signedChallenge: "{challenge}|{password}"}}
      ) {{
        jwtClaim
        }}
      }}
  '''

attrib_by_id = '''
  query attribById {{
    attribute(id: "{attrib_id}") {{
      id
      dataType
      description
      displayName
      updatedTimestamp
      createdTimestamp
      }}
    }} 
  '''

update_timeseries = '''
  mutation timeseries_update {{
    replaceTimeSeriesRange(
      input: {{
        attributeOrTagId: "{attrib_id}"
        entries: [
          {stamped_data}
        ]
        startTime: "{start_time}"
        endTime: "{end_time}"
      }}
    ) {{
      clientMutationId
      json
    }}
  }}
  '''