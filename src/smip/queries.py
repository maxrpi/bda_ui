
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

update_lot_series = '''
  mutation lot_series_update {{
    replaceTimeSeriesRange(
      input: {{
        attributeOrTagId: "{attrib_id}"
        entries: [
          {entries}
        ]
        startTime: "{start_time}"
        endTime: "{end_time}"
      }}
    ) {{
      json
    }}
  }}
  '''

get_timeseries = '''
  query query_num_{index} {{
    getRawHistoryDataWithSampling(
            maxSamples: {max_samples} 
            ids: "{attrib_id}"
            startTime: "{start_time}"
            endTime: "{end_time}"
    ) {{
        ts
        floatvalue
    }}
}}
'''

get_lot_series = '''
  query get_lot_data_{index} {{
    attribute(id: "{attrib_id}") {{
      getTimeSeries(
        startTime: "{start_time}"
        endTime: "{end_time}"
      ) {{
        ts
        objectvalue
      }}
    }}
  }}
  '''

get_raw_attribute_data = '''
  query firstTime {{
    attribute(id: "{attrib_id}") {{
      getTimeSeries(
        maxSamples: 0
        startTime: "{start_time}"
        endTime: "{end_time}"
      ) {{
        ts
        floatvalue
      }}
    }}
  }}
  '''