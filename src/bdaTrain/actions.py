import dateutil.parser
from datetime import timedelta

import refresher
import bda_service
from smip import get_timeseries_array, smip_auth

def add_attribute(page, attrib_id, attrib_name, window):
  
  if attrib_name not in page.known_attributes:
    page.avail_keys.append(attrib_name)
    page.known_attributes[attrib_name] = attrib_id
    window['-ATTRIBUTE_LIST-'].update(values=page.avail_keys)
    new_index = page.avail_keys.index(attrib_name)
    window['-ATTRIBUTE_LIST-'].update(set_to_index=[new_index],
    scroll_to_index=new_index)
  else:
    page.known_attributes[attrib_name] = attrib_id

def avail_to_inputs(page, event, values, window):
  selected_keys = values['-ATTRIBUTE_LIST-']
  selected_indexes = window['-ATTRIBUTE_LIST-'].get_indexes()
  for index in selected_indexes:
    page.inputs_keys.append(page.avail_keys.pop(index))
  window['-ATTRIBUTE_LIST-'].update(page.avail_keys)
  window['-INPUTS_LIST-'].update(page.inputs_keys)

def avail_to_outputs(page, event, values, window):
  selected_keys = values['-ATTRIBUTE_LIST-']
  selected_indexes = window['-ATTRIBUTE_LIST-'].get_indexes()
  for index in selected_indexes:
    page.outputs_keys.append(page.avail_keys.pop(index))
  window['-ATTRIBUTE_LIST-'].update(page.avail_keys)
  window['-OUTPUTS_LIST-'].update(page.outputs_keys)

def inputs_to_avail(page, event, values, window):
  selected_indexes = window['-INPUTS_LIST-'].get_indexes()
  for index in selected_indexes:
    page.avail_keys.append(page.inputs_keys.pop(index))
  window['-INPUTS_LIST-'].update(page.inputs_keys)
  window['-ATTRIBUTE_LIST-'].update(page.avail_keys)

def outputs_to_avail(page, event, values, window):
  selected_indexes = window['-OUTPUTS_LIST-'].get_indexes()
  for index in selected_indexes:
    page.avail_keys.append(page.outputs_keys.pop(index))
  window['-OUTPUTS_LIST-'].update(page.outputs_keys)
  window['-ATTRIBUTE_LIST-'].update(page.avail_keys)

def create_attrib_id_list(page):
  attrib_id_list = [page.known_attributes[key] for key in page.inputs_keys + page.outputs_keys]
  attrib_id_list_string = ",".join(attrib_id_list)
  return attrib_id_list

def parseTime(key, dateStr, window):
  try:
    dateObj = dateutil.parser.parse(dateStr)
  except dateutil.parser.ParserError as err:
    window[key].update(select=True)
    return None
  window[key].update(value=dateObj.strftime("%Y-%m-%dT%H:%M:%SZ"))
  return dateObj

def init_server(page, event, values, window):
  service_url = values["-BDA_URL-"]
  secret = values["-SERVER_SECRET-"]
  admin = bda_service.User("admin", "adminpassword")
  page.service = bda_service.BDAService(service_url, secret, admin)
  page.service.initialize_server()
  page.service.login_user(admin)
  refresher.refresh_daemon.add_task(admin)

def create_user(page, event, values, window):
  username = values["-BDA_USER-"]
  password = values["-BDA_PASSWORD-"]
  page._user = bda_service.User(username, password)
  page.service.add_user(user)
  return page._user

def login_user(page, event, values, window):
  page.service.login_user(page._user)
  refresher.refresh_daemon.add_task(page._user)
  window['-BDA_EXPIRES-'].update(page._user.auth_expiration)

def parse_start(page, event, values, window):
  key = "-START_TIME-"
  page.startTimeObj = parseTime(key, values[key], window)

def parse_end(page, event, values, window):
  key = "-END_TIME-"
  page.endTimeObj = parseTime(key, values[key], window)

def set_max_time_range(page, event, values, window):
  page.startTimeObj = parseTime("-START_TIME-", "1900-01-01", window)
  page.endTimeObj = parseTime("-END_TIME-", "2100-01-01", window)

def download_dataset(page, event, values, window):
  filename = values['-DOWNLOAD_REQUEST_FILENAME-']
  df = get_timeseries_array(smip_auth['url'],
    smip_auth['token'], create_attrib_id_list(page),
    page.startTimeObj.strftime("%Y-%m-%d %H:%M:%S+00"),
    page.endTimeObj.strftime("%Y-%m-%d %H:%M:%S+00"),
    values['-NUMBER_SAMPLES-'],
    timedelta(seconds=int(values['-SAMPLE_PERIOD-'])))
  
  with open(filename, "w") as fd:
    fd.write(df.to_csv(index=False, date_format="%Y-%m-%d %H:%M:%S+00"))
    fd.close()
    
def train_mko(page, event, values, window):
    if page.user is None:
      return True
    model_name = values['-MKOname-']
    claim_check = bda_service.create_mko(page.service,page.user, model_name)
    mko = bda_service.redeem_claim_check(page.service, page.user, claim_check)
    return True

actions = { 
  "-INIT_SERVER-": init_server,
  "-CREATE_USER-": create_user,
  "-LOGIN_USER-" : login_user,
  "-SEND_INPUT-" : avail_to_inputs,
  "-SEND_OUTPUT-": avail_to_outputs,
  "-RETURN_INPUT-":  inputs_to_avail,
  "-RETURN_OUTPUT-": outputs_to_avail,
  "-PARSE_START-": parse_start,
  "-PARSE_END-"  : parse_end,
  "START_TIME" + "RETURN": parse_start,
  "END_TIME"   + "RETURN": parse_end,
  "-SET_MAX_RANGE-" : set_max_time_range,
  "-DOWNLOAD_DATASET_FILENAME-": download_dataset,
  "-TRAIN_MKO-"  : train_mko
}
