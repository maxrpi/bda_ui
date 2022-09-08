import PySimpleGUI as sg
import pandas as pd
import dateutil.parser
import datetime
import bda_service
import refresher
from bdaTrain.layout import layout
from footer import statusbar

class bt():
  known_attributes = {}
  avail_keys = list(known_attributes.keys())
  inputs_keys = []
  outputs_keys = []
  smip_auth = {}
  startTimeObj : datetime.datetime = None
  endTimeObj : datetime.datetime = None
  user : bda_service.User = None
  settings = {}

def assign_settings(my_settings, window):
  bt.settings = my_settings
  if bt.settings['url'] is not None: window['-BDA_URL-'].update(bt.settings['url']) 
  if bt.settings['username'] is not None: window['-BDA_USER-'].update(bt.settings['username']) 
  if bt.settings['password'] is not None: window['-BDA_PASSWORD-'].update(bt.settings['password']) 
  if bt.settings['server_secret'] is not None: window['-SERVER_SECRET-'].update(bt.settings['server_secret']) 
  if bt.settings['start_time'] is not None: window['-START_TIME-'].update(bt.settings['start_time']) 
  if bt.settings['end_time'] is not None: window['-END_TIME-'].update(bt.settings['end_time']) 
  if bt.settings['sample_period'] is not None: window['-SAMPLE_PERIOD-'].update(bt.settings['sample_period']) 
  if bt.settings['number_samples'] is not None: window['-NUMBER_SAMPLES-'].update(bt.settings['number_samples']) 

def set_bindings(window):
  window['-PARSE_START-'].bind('<KeyPress-Return>','RETURN')
  window['-PARSE_END-'].bind('<KeyPress-Return>','RETURN')
  window['-SAMPLE_PERIOD-'].bind('<KeyPress-Return>','RETURN')
  window['-NUMBER_SAMPLES-'].bind('<KeyPress-Return>','RETURN')

def set_smip_auth(url, username, role, password, token):
  bt.smip_auth['url'] = url
  bt.smip_auth['username'] = username
  bt.smip_auth['role'] = role
  bt.smip_auth['password'] = password
  bt.smip_auth['token'] = token

def add_attribute(attrib_id, attrib_name, window):
  
  if attrib_name not in bt.known_attributes:
    bt.avail_keys.append(attrib_name)
    bt.known_attributes[attrib_name] = attrib_id
    window['-ATTRIBUTE_LIST-'].update(values=bt.avail_keys)
    new_index = bt.avail_keys.index(attrib_name)
    window['-ATTRIBUTE_LIST-'].update(set_to_index=[new_index],
    scroll_to_index=new_index)

  else:
    statusbar.update("Updating name {} to id {}".format(attrib_name, attrib_id))
    bt.known_attributes[attrib_name] = attrib_id


def avail_to_inputs(values, window):
  selected_indexes = window['-ATTRIBUTE_LIST-'].get_indexes()
  for index in selected_indexes:
    bt.inputs_keys.append(bt.avail_keys.pop(index))
  window['-ATTRIBUTE_LIST-'].update(bt.avail_keys)
  window['-INPUTS_LIST-'].update(bt.inputs_keys)

def avail_to_outputs(values, window):
  selected_keys = values['-ATTRIBUTE_LIST-']
  selected_indexes = window['-ATTRIBUTE_LIST-'].get_indexes()
  for index in selected_indexes:
    bt.outputs_keys.append(bt.avail_keys.pop(index))
  window['-ATTRIBUTE_LIST-'].update(bt.avail_keys)
  window['-OUTPUTS_LIST-'].update(bt.outputs_keys)

def inputs_to_avail(values, window):
  selected_indexes = window['-INPUTS_LIST-'].get_indexes()
  for index in selected_indexes:
    bt.avail_keys.append(bt.inputs_keys.pop(index))
  window['-INPUTS_LIST-'].update(bt.inputs_keys)
  window['-ATTRIBUTE_LIST-'].update(bt.avail_keys)

def outputs_to_avail(values, window):
  selected_indexes = window['-OUTPUTS_LIST-'].get_indexes()
  for index in selected_indexes:
    bt.avail_keys.append(bt.outputs_keys.pop(index))
  window['-OUTPUTS_LIST-'].update(bt.outputs_keys)
  window['-ATTRIBUTE_LIST-'].update(bt.avail_keys)

def parseTime(key, dateStr, window) -> 'datetime.datetime':
  try:
    dateObj = dateutil.parser.parse(dateStr)
  except dateutil.parser.ParserError as err:
    window[key].update(select=True)
    return None
  window[key].update(value=dateObj.strftime("%Y-%m-%dT%H:%M:%SZ"), text_color="blue")
  return dateObj
  
def create_attrib_id_list():
  attrib_id_list = [bt.known_attributes[key] for key in bt.inputs_keys + bt.outputs_keys]
  attrib_id_list_string = ",".join(attrib_id_list)
  return attrib_id_list

def samples_and_periods(samples, period, priority="s"):
  s = int(samples)
  p = float(period)
  if bt.endTimeObj == None or bt.startTimeObj == None:
    return s, p
  interval = bt.endTimeObj.timestamp() - bt.startTimeObj.timestamp()
  if p == 0:
    if s == 0:
      s = 10
    p = interval / float(s)
  elif s == 0:
    s = interval / p
  elif priority == "p":
    s = int(interval / p)
    p = interval / float(s)
  else:
    p = interval / float(s)

  return s, p


def init_server(values):
  
  service_url = values["-BDA_URL-"]
  secret = values["-SERVER_SECRET-"]
  if not bda_service.service.initialized:
    admin = bda_service.User("admin", "adminpassword")
    bda_service.service.set_data(service_url, secret, admin)
  elif bda_service.service.baseurl != service_url:
    bda_service.service.set_baseurl(service_url)
  try:
    bda_service.service.initialize_server()
    bda_service.service.login_user(bda_service.service.admin)
    statusbar.update("Service is initialized")
    refresher.refresh_daemon.add_task(bda_service.service.admin)
  except Exception as err:
    statusbar.update("Problems initializing server: {}".format(err))

def create_user(values):
  username = values["-BDA_USER-"]
  password = values["-BDA_PASSWORD-"]
  user = bda_service.User(username, password)
  bda_service.service.add_user(user)
  return user


def handler(event, values, window, get_timeseries_array, add_mko_to_infer):
  if event == "-INIT_SERVER-":
    try:
      init_server(values)
    except Exception as err:
      print(err)
    return True
  if event == "-CREATE_USER-":
    try:
      bt.user = create_user(values)
    except Exception as err:
      print(err)
    return True

  if event == "-LOG_IN_BDA-":
    try:
      bda_service.service.login_user(bt.user)
      bda_service.service.set_current_user(bt.user)
      refresher.refresh_daemon.add_task(bt.user)
      window['-BDA_EXPIRES-'].update(bt.user.auth_expiration)
      statusbar.update("logged {} in on BDA server".format(bt.user.username))
    except Exception as err:
      statusbar.update("Could not login {} on server: {}".format(u.username, err))
    return True

  if event == "-INPUT_SEND-":
    avail_to_inputs(values, window)
    return True
  if event == "-RETURN_INPUT-":
    inputs_to_avail(values, window)
    return True
  if event == "-OUTPUT_SEND-":
    avail_to_outputs(values, window)
    return True
  if event == "-RETURN_OUTPUT-":
    outputs_to_avail(values, window)
    return True
  if event == "-PARSE_START-" or event == "START_TIME" + "RETURN":
    key = "-START_TIME-"
    bt.startTimeObj = parseTime(key, values[key], window)
    bt.settings["start_time"] = values[key]
    s, p = samples_and_periods(values['-NUMBER_SAMPLES-'], values['-SAMPLE_PERIOD-'])
    window['-NUMBER_SAMPLES-'].update(str(s))
    window['-SAMPLE_PERIOD-'].update(str(p))
    bt.settings['number_samples'] = s
    bt.settings['period'] = p
    return True
  if event == "-PARSE_END-" or event == "END_TIME" + "RETURN":
    key = "-END_TIME-"
    bt.endTimeObj = parseTime(key, values[key], window)
    bt.settings["end_time"] = values[key]
    s, p = samples_and_periods(values['-NUMBER_SAMPLES-'], values['-SAMPLE_PERIOD-'])
    window['-NUMBER_SAMPLES-'].update(str(s))
    window['-SAMPLE_PERIOD-'].update(str(p))
    bt.settings['number_samples'] = s
    bt.settings['period'] = p
    return True
  if event == "-SET_MAX_RANGE-":
    bt.startTimeObj = parseTime("-START_TIME-", "1900-01-01", window)
    bt.endTimeObj = parseTime("-END_TIME-", "2100-01-01", window)
    s, p = samples_and_periods(values['-NUMBER_SAMPLES-'], values['-SAMPLE_PERIOD-'])
    window['-NUMBER_SAMPLES-'].update(str(s))
    window['-SAMPLE_PERIOD-'].update(str(p))
    bt.settings['number_samples'] = s
    bt.settings['period'] = p
    return True
  if event == "-NUMBER_SAMPLES-" + "RETURN":
    s, p = samples_and_periods(values['-NUMBER_SAMPLES-'], values['-SAMPLE_PERIOD-'], priority="s")
    window['-NUMBER_SAMPLES-'].update(str(s))
    window['-SAMPLE_PERIOD-'].update(str(p))
    bt.settings['number_samples'] = s
    bt.settings['period'] = p
    return True
  if event == "-SAMPLE_PERIOD-" + "RETURN":
    s, p = samples_and_periods(values['-NUMBER_SAMPLES-'], values['-SAMPLE_PERIOD-'], priority="p")
    window['-NUMBER_SAMPLES-'].update(str(s))
    window['-SAMPLE_PERIOD-'].update(str(p))
    bt.settings['number_samples'] = s
    bt.settings['period'] = p
    return True

  if event == "-DOWNLOAD_REQUEST_FILENAME-":
    filename = values['-DOWNLOAD_REQUEST_FILENAME-']
    df = get_timeseries_array(bt.smip_auth['url'],
      bt.smip_auth['token'], create_attrib_id_list(),
      bt.startTimeObj.strftime("%Y-%m-%d %H:%M:%S+00"),
      bt.endTimeObj.strftime("%Y-%m-%d %H:%M:%S+00"),
      values['-NUMBER_SAMPLES-'],
      datetime.timedelta(seconds=int(float(values['-SAMPLE_PERIOD-']))))
    
    with open(filename, "w") as fd:
      fd.write(df.to_csv(index=False, date_format="%Y-%m-%d %H:%M:%S+00"))
      fd.close()
      
    return True

  if event == "-TRAIN_MKO-":
    if bda_service.service.current_user.logged_in is False:
      return True
    model_name = values['-MKOname-']
    mko = bda_service.MKO(model_name, bt.user, bda_service.service, auto_progress=True)
    inputs = [str(bt.known_attributes[key]) for key in bt.inputs_keys]
    outputs = [str(bt.known_attributes[key]) for key in bt.outputs_keys]
    mko.set_inputs_and_outputs(inputs, outputs)
    mko.set_time_parameters(
      bt.startTimeObj,
      bt.endTimeObj,
      values['-SAMPLE_PERIOD-'],
      values['-NUMBER_SAMPLES-']
    )
    mko.set_smip_auth(bt.smip_auth)
    add_mko_to_infer(mko, window)
    refresher.refresh_daemon.add_task(mko)

    
    return True

  return False