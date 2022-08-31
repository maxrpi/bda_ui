import PySimpleGUI as sg
import pandas as pd
import dateutil.parser
import datetime
import bda_service
import refresher
from bdaTrain.layout import layout
from footer import statusbar

known_attributes = {}
avail_keys = list(known_attributes.keys())
inputs_keys = []
outputs_keys = []
smip_auth = {}
startTimeObj = None
endTimeObj = None
my_settings_copy = {}

def assign_settings(settings, window):
  global my_settings_copy
  my_settings_copy = settings
  if settings['url'] is not None: window['-BDA_URL-'].update(settings['url']) 
  if settings['username'] is not None: window['-BDA_USER-'].update(settings['username']) 
  if settings['password'] is not None: window['-BDA_PASSWORD-'].update(settings['password']) 
  if settings['server_secret'] is not None: window['-SERVER_SECRET-'].update(settings['server_secret']) 
  if settings['start_time'] is not None: window['-START_TIME-'].update(settings['start_time']) 
  if settings['end_time'] is not None: window['-END_TIME-'].update(settings['end_time']) 
  if settings['sample_period'] is not None: window['-SAMPLE_PERIOD-'].update(settings['sample_period']) 
  if settings['number_samples'] is not None: window['-NUMBER_SAMPLES-'].update(settings['number_samples']) 

def set_bindings(window):
  window['-PARSE_START-'].bind('<KeyPress-Return>','RETURN')
  window['-PARSE_END-'].bind('<KeyPress-Return>','RETURN')
  window['-SAMPLE_PERIOD-'].bind('<KeyPress-Return>','RETURN')
  window['-NUMBER_SAMPLES-'].bind('<KeyPress-Return>','RETURN')

def set_smip_auth(url, username, role, password, token):
  global smip_auth
  smip_auth['url'] = url
  smip_auth['username'] = username
  smip_auth['role'] = role
  smip_auth['password'] = password
  smip_auth['token'] = token

def add_attribute(attrib_id, attrib_name, window):
  global avail_keys
  global known_attributes
  
  if attrib_name not in known_attributes:
    avail_keys.append(attrib_name)
    known_attributes[attrib_name] = attrib_id
    window['-ATTRIBUTE_LIST-'].update(values=avail_keys)
    new_index = avail_keys.index(attrib_name)
    window['-ATTRIBUTE_LIST-'].update(set_to_index=[new_index],
    scroll_to_index=new_index)

  else:
    print("Updating name {} to id {}".format(attrib_name, attrib_id))
    known_attributes[attrib_name] = attrib_id


def avail_to_inputs(values, window):
  global known_attributes
  global avail_keys
  global inputs_keys
  selected_indexes = window['-ATTRIBUTE_LIST-'].get_indexes()
  for index in selected_indexes:
    inputs_keys.append(avail_keys.pop(index))
  window['-ATTRIBUTE_LIST-'].update(avail_keys)
  window['-INPUTS_LIST-'].update(inputs_keys)

def avail_to_outputs(values, window):
  global known_attributes
  global avail_keys
  global outputs_keys
  selected_keys = values['-ATTRIBUTE_LIST-']
  selected_indexes = window['-ATTRIBUTE_LIST-'].get_indexes()
  for index in selected_indexes:
    outputs_keys.append(avail_keys.pop(index))
  window['-ATTRIBUTE_LIST-'].update(avail_keys)
  window['-OUTPUTS_LIST-'].update(outputs_keys)

def inputs_to_avail(values, window):
  global known_attributes
  global avail_keys
  global inputs_keys
  selected_indexes = window['-INPUTS_LIST-'].get_indexes()
  for index in selected_indexes:
    avail_keys.append(inputs_keys.pop(index))
  window['-INPUTS_LIST-'].update(inputs_keys)
  window['-ATTRIBUTE_LIST-'].update(avail_keys)

def outputs_to_avail(values, window):
  global known_attributes
  global avail_keys
  global outputs_keys
  selected_indexes = window['-OUTPUTS_LIST-'].get_indexes()
  for index in selected_indexes:
    avail_keys.append(outputs_keys.pop(index))
  window['-OUTPUTS_LIST-'].update(outputs_keys)
  window['-ATTRIBUTE_LIST-'].update(avail_keys)

def parseTime(key, dateStr, window):
  try:
    dateObj = dateutil.parser.parse(dateStr)
  except dateutil.parser.ParserError as err:
    window[key].update(select=True)
    return None
  window[key].update(value=dateObj.strftime("%Y-%m-%dT%H:%M:%SZ"), text_color="blue")
  return dateObj
  
def create_attrib_id_list():
  global known_attributes, inputs_keys, outputs_keys
  attrib_id_list = [known_attributes[key] for key in inputs_keys + outputs_keys]
  attrib_id_list_string = ",".join(attrib_id_list)
  return attrib_id_list

def samples_and_periods(samples, period, priority="s"):
  s = int(samples)
  p = float(period)
  if endTimeObj == None or startTimeObj == None:
    return s, p
  interval = endTimeObj.timestamp() - startTimeObj.timestamp()
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
  global service
  service_url = values["-BDA_URL-"]
  secret = values["-SERVER_SECRET-"]
  admin = bda_service.User("admin", "adminpassword")
  service = bda_service.BDAService(service_url, secret, admin)
  bda_service.bda_service = service
  service.initialize_server()
  service.login_user(admin)
  refresher.refresh_daemon.add_task(admin)

def create_user(values):
  global service, user
  username = values["-BDA_USER-"]
  password = values["-BDA_PASSWORD-"]
  user = bda_service.User(username, password)
  service.add_user(user)
  return user


def handler(event, values, window, get_timeseries_array, add_mko_to_infer):
  global startTimeObj, endTimeObj, service, user
  if event == "-INIT_SERVER-":
    try:
      init_server(values)
    except Exception as err:
      print(err)
    return True
  if event == "-CREATE_USER-":
    try:
      user = create_user(values)
    except Exception as err:
      print(err)
    return True

  if event == "-LOG_IN_BDA-":
    try:
      service.login_user(user)
      service.set_current_user(user)
      refresher.refresh_daemon.add_task(user)
      window['-BDA_EXPIRES-'].update(user.auth_expiration)
    except Exception as err:
      print(err)
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
    startTimeObj = parseTime(key, values[key], window)
    my_settings_copy["start_time"] = values[key]
    s, p = samples_and_periods(values['-NUMBER_SAMPLES-'], values['-SAMPLE_PERIOD-'])
    window['-NUMBER_SAMPLES-'].update(str(s))
    window['-SAMPLE_PERIOD-'].update(str(p))
    my_settings_copy['number_samples'] = s
    my_settings_copy['period'] = p
    return True
  if event == "-PARSE_END-" or event == "END_TIME" + "RETURN":
    key = "-END_TIME-"
    endTimeObj = parseTime(key, values[key], window)
    my_settings_copy["end_time"] = values[key]
    s, p = samples_and_periods(values['-NUMBER_SAMPLES-'], values['-SAMPLE_PERIOD-'])
    window['-NUMBER_SAMPLES-'].update(str(s))
    window['-SAMPLE_PERIOD-'].update(str(p))
    my_settings_copy['number_samples'] = s
    my_settings_copy['period'] = p
    return True
  if event == "-SET_MAX_RANGE-":
    startTimeObj = parseTime("-START_TIME-", "1900-01-01", window)
    endTimeObj = parseTime("-END_TIME-", "2100-01-01", window)
    s, p = samples_and_periods(values['-NUMBER_SAMPLES-'], values['-SAMPLE_PERIOD-'])
    window['-NUMBER_SAMPLES-'].update(str(s))
    window['-SAMPLE_PERIOD-'].update(str(p))
    my_settings_copy['number_samples'] = s
    my_settings_copy['period'] = p
    return True
  if event == "-NUMBER_SAMPLES-" + "RETURN":
    s, p = samples_and_periods(values['-NUMBER_SAMPLES-'], values['-SAMPLE_PERIOD-'], priority="s")
    window['-NUMBER_SAMPLES-'].update(str(s))
    window['-SAMPLE_PERIOD-'].update(str(p))
    my_settings_copy['number_samples'] = s
    my_settings_copy['period'] = p
    return True
  if event == "-SAMPLE_PERIOD-" + "RETURN":
    s, p = samples_and_periods(values['-NUMBER_SAMPLES-'], values['-SAMPLE_PERIOD-'], priority="p")
    window['-NUMBER_SAMPLES-'].update(str(s))
    window['-SAMPLE_PERIOD-'].update(str(p))
    my_settings_copy['number_samples'] = s
    my_settings_copy['period'] = p
    return True

  if event == "-DOWNLOAD_REQUEST_FILENAME-":
    filename = values['-DOWNLOAD_REQUEST_FILENAME-']
    df = get_timeseries_array(smip_auth['url'],
      smip_auth['token'], create_attrib_id_list(),
      startTimeObj.strftime("%Y-%m-%d %H:%M:%S+00"),
      endTimeObj.strftime("%Y-%m-%d %H:%M:%S+00"),
      values['-NUMBER_SAMPLES-'],
      datetime.timedelta(seconds=int(float(values['-SAMPLE_PERIOD-']))))
    
    with open(filename, "w") as fd:
      fd.write(df.to_csv(index=False, date_format="%Y-%m-%d %H:%M:%S+00"))
      fd.close()
      
    return True

  if event == "-TRAIN_MKO-":
    if user is None:
      return True
    model_name = values['-MKOname-']
    mko = bda_service.MKO(model_name, user, service, auto_progress=True)
    inputs = [str(known_attributes[key]) for key in inputs_keys]
    outputs = [str(known_attributes[key]) for key in outputs_keys]
    mko.set_inputs_and_outputs(inputs, outputs)
    mko.set_time_parameters(
      startTimeObj,
      endTimeObj,
      values['-SAMPLE_PERIOD-'],
      values['-NUMBER_SAMPLES-']
    )
    mko.set_smip_auth(smip_auth)
    add_mko_to_infer(mko, window)
    refresher.refresh_daemon.add_task(mko)

    
    return True

  return False