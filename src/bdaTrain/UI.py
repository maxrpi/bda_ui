import PySimpleGUI as sg
import pandas as pd
import dateutil.parser
import datetime
import bda_service
import refresher
from bdaTrain.layout import layout
from footer import statusbar

class ts():
  known_features = {}
  avail_keys = list(known_features.keys())
  inputs_keys = []
  outputs_keys = []
  prefix = "TS"
  startTimeObj : datetime.datetime = None
  endTimeObj : datetime.datetime = None
class ls():
  feature_container_attrib = -1
  feature_container_name = ""
  all_lots = True
  known_features = {}
  avail_keys = list(known_features.keys())
  inputs_keys = []
  outputs_keys = []
  prefix = "LS"
  start_key = None
  end_key = None
class bt():
  smip_auth = {}
  user : bda_service.User = None
  settings = {}

def assign_settings(my_settings, window):
  bt.settings = my_settings
  if bt.settings['url'] is not None: window['-BDA_URL-'].update(bt.settings['url']) 
  if bt.settings['username'] is not None: window['-BDA_USER-'].update(bt.settings['username']) 
  if bt.settings['password'] is not None: window['-BDA_PASSWORD-'].update(bt.settings['password']) 
  if bt.settings['server_secret'] is not None: window['-SERVER_SECRET-'].update(bt.settings['server_secret']) 
  if bt.settings['start_time'] is not None: window['-TS_START_TIME-'].update(bt.settings['start_time']) 
  if bt.settings['end_time'] is not None: window['-TS_END_TIME-'].update(bt.settings['end_time']) 
  if bt.settings['sample_period'] is not None: window['-TS_SAMPLE_PERIOD-'].update(bt.settings['sample_period']) 
  if bt.settings['number_samples'] is not None: window['-TS_NUMBER_SAMPLES-'].update(bt.settings['number_samples']) 

def set_bindings(window):
  window['-TS_PARSE_START-'].bind('<KeyPress-Return>','RETURN')
  window['-TS_PARSE_END-'].bind('<KeyPress-Return>','RETURN')
  window['-TS_SAMPLE_PERIOD-'].bind('<KeyPress-Return>','RETURN')
  window['-TS_NUMBER_SAMPLES-'].bind('<KeyPress-Return>','RETURN')

def set_smip_auth(url, username, role, password, token):
  bt.smip_auth['url'] = url
  bt.smip_auth['username'] = username
  bt.smip_auth['role'] = role
  bt.smip_auth['password'] = password
  bt.smip_auth['token'] = token

def add_timeseries(attrib_id, attrib_name, window):
  
  if attrib_name not in ts.known_features:
    ts.avail_keys.append(attrib_name)
    ts.known_features[attrib_name] = attrib_id
    window['-TS_FEATURE_LIST-'].update(values=ts.avail_keys)
    new_index = ts.avail_keys.index(attrib_name)
    window['-TS_FEATURE_LIST-'].update(set_to_index=[new_index],
    scroll_to_index=new_index)
  else:
    statusbar.update("Updating name {} to id {}".format(attrib_name, attrib_id))
    ts.known_features[attrib_name] = attrib_id
  
def add_lot_series(attrib_id, attrib_name, feature_list, window):
  ls.feature_container_attrib = int(attrib_id)
  ls.feature_container_name = attrib_name 
  ls.known_features = feature_list
  ls.avail_keys = feature_list
  ls.inputs_keys = []
  ls.outputs_keys = []
  window['-LS_LOT_HOLDER_ATTRIBUTE-'].update(ls.feature_container_attrib)
  window['-LS_LOT_HOLDER_NAME-'].update(ls.feature_container_name)
  window['-LS_FEATURE_LIST-'].update(values=ls.avail_keys)
  window['-LS_INPUTS_LIST-'].update(values=ls.inputs_keys)
  window['-LS_OUTPUTS_LIST-'].update(values=ls.outputs_keys)

def avail_to_inputs(values, window, tab):
  selected_indexes = window[f'-{tab.prefix}_FEATURE_LIST-'].get_indexes()
  for index in selected_indexes:
    tab.inputs_keys.append(tab.avail_keys.pop(index))
  window[f'-{tab.prefix}_FEATURE_LIST-'].update(tab.avail_keys)
  window[f'-{tab.prefix}_INPUTS_LIST-'].update(tab.inputs_keys)

def avail_to_outputs(values, window, tab):
  selected_keys = values[f'-{tab.prefix}_FEATURE_LIST-']
  selected_indexes = window[f'-{tab.prefix}_FEATURE_LIST-'].get_indexes()
  for index in selected_indexes:
    tab.outputs_keys.append(tab.avail_keys.pop(index))
  window[f'-{tab.prefix}_FEATURE_LIST-'].update(tab.avail_keys)
  window[f'-{tab.prefix}_OUTPUTS_LIST-'].update(tab.outputs_keys)

def inputs_to_avail(values, window, tab):
  selected_indexes = window[f'-{tab.prefix}_INPUTS_LIST-'].get_indexes()
  for index in selected_indexes:
    tab.avail_keys.append(tab.inputs_keys.pop(index))
  window[f'-{tab.prefix}_INPUTS_LIST-'].update(tab.inputs_keys)
  window[f'-{tab.prefix}_FEATURE_LIST-'].update(tab.avail_keys)

def outputs_to_avail(values, window, tab):
  selected_indexes = window[f'-{tab.prefix}_OUTPUTS_LIST-'].get_indexes()
  for index in selected_indexes:
    tab.avail_keys.append(tab.outputs_keys.pop(index))
  window[f'-{tab.prefix}_OUTPUTS_LIST-'].update(tab.outputs_keys)
  window[f'-{tab.prefix}_FEATURE_LIST-'].update(tab.avail_keys)

def parseTime(key, dateStr, window) -> 'datetime.datetime':
  try:
    dateObj = dateutil.parser.parse(dateStr)
  except dateutil.parser.ParserError as err:
    window[key].update(select=True)
    return None
  window[key].update(value=dateObj.strftime("%Y-%m-%dT%H:%M:%SZ"), text_color="blue")
  return dateObj
  
def create_feature_id_list_ts(tab):
  attrib_id_list = [tab.known_features[key] for key in tab.inputs_keys + tab.outputs_keys]
  return attrib_id_list

def samples_and_periods(samples, period, priority="s"):
  s = int(samples)
  p = float(period)
  if ts.endTimeObj == None or ts.startTimeObj == None:
    return s, p
  interval = ts.endTimeObj.timestamp() - ts.startTimeObj.timestamp()
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
  bt.settings['url'] = service_url
  secret = values["-SERVER_SECRET-"]
  bt.settings['server_secret'] = secret
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
  bt.settings['username'] = username
  bt.settings['password'] = password
  user = bda_service.User(username, password)
  bda_service.service.add_user(user)
  return user


def handler(event, values, window, get_timeseries_array, get_lot_series, add_mko_to_infer):
  ### SERVICE EVENTS SECTION ###
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
      statusbar.update("Could not login {} on server: {}".format(bt.user.username, err))
    return True

  ### TIMESERIES EVENTS SECTION ###
  if event == "-TS_INPUT_SEND-":
    avail_to_inputs(values, window, ts)
    return True
  if event == "-TS_RETURN_INPUT-":
    inputs_to_avail(values, window, ts)
    return True
  if event == "-TS_OUTPUT_SEND-":
    avail_to_outputs(values, window, ts)
    return True
  if event == "-TS_RETURN_OUTPUT-":
    outputs_to_avail(values, window, ts)
    return True
  if event == "-TS_PARSE_START-" or event == "-TS_START_TIME" + "RETURN":
    key = "-TS_START_TIME-"
    ts.startTimeObj = parseTime(key, values[key], window)
    bt.settings["start_time"] = values[key]
    s, p = samples_and_periods(values['-TS_NUMBER_SAMPLES-'], values['-TS_SAMPLE_PERIOD-'])
    window['-TS_NUMBER_SAMPLES-'].update(str(s))
    window['-TS_SAMPLE_PERIOD-'].update(str(p))
    bt.settings['number_samples'] = s
    bt.settings['period'] = p
    return True
  if event == "-TS_PARSE_END-" or event == "-TS_END_TIME" + "RETURN":
    key = "-TS_END_TIME-"
    ts.endTimeObj = parseTime(key, values[key], window)
    bt.settings["end_time"] = values[key]
    s, p = samples_and_periods(values['-TS_NUMBER_SAMPLES-'], values['-TS_SAMPLE_PERIOD-'])
    window['-TS_NUMBER_SAMPLES-'].update(str(s))
    window['-TS_SAMPLE_PERIOD-'].update(str(p))
    bt.settings['number_samples'] = s
    bt.settings['period'] = p
    return True
  if event == "-TS_SET_MAX_RANGE-":
    ts.startTimeObj = parseTime("-TS_START_TIME-", "1900-01-01", window)
    ts.endTimeObj = parseTime("-TS_END_TIME-", "2100-01-01", window)
    s, p = samples_and_periods(values['-TS_NUMBER_SAMPLES-'], values['-TS_SAMPLE_PERIOD-'])
    window['-TS_NUMBER_SAMPLES-'].update(str(s))
    window['-TS_SAMPLE_PERIOD-'].update(str(p))
    bt.settings['number_samples'] = s
    bt.settings['period'] = p
    return True
  if event == "-TS_NUMBER_SAMPLES-" + "RETURN":
    s, p = samples_and_periods(values['-TS_NUMBER_SAMPLES-'], values['-TS_SAMPLE_PERIOD-'], priority="s")
    window['-TS_NUMBER_SAMPLES-'].update(str(s))
    window['-TS_SAMPLE_PERIOD-'].update(str(p))
    bt.settings['number_samples'] = s
    bt.settings['period'] = p
    return True
  if event == "-TS_SAMPLE_PERIOD-" + "RETURN":
    s, p = samples_and_periods(values['-TS_NUMBER_SAMPLES-'], values['-TS_SAMPLE_PERIOD-'], priority="p")
    window['-TS_NUMBER_SAMPLES-'].update(str(s))
    window['-TS_SAMPLE_PERIOD-'].update(str(p))
    bt.settings['number_samples'] = s
    bt.settings['period'] = p
    return True
  if event == "-TS_DOWNLOAD_REQUEST_FILENAME-":
    filename = values['-TS_DOWNLOAD_REQUEST_FILENAME-']
    df = get_timeseries_array(bt.smip_auth['url'],
      bt.smip_auth['token'], create_feature_id_list_ts(ts),
      ts.startTimeObj.strftime("%Y-%m-%d %H:%M:%S+00"),
      ts.endTimeObj.strftime("%Y-%m-%d %H:%M:%S+00"),
      values['-TS_NUMBER_SAMPLES-'],
      datetime.timedelta(seconds=int(float(values['-TS_SAMPLE_PERIOD-']))))
    time_as_timestamp = window['-TS_TIME_AS_TIMESTAMP-'].get()
    df.dropna(inplace=True)
    if time_as_timestamp:
      df['ts'] = pd.to_datetime(df.ts)
      df['ts'] = df.ts.astype('int64') //  10**9
    with open(filename, "w") as fd:
      fd.write(df.to_csv(index=False, date_format="%Y-%m-%d %H:%M:%S+00"))
      fd.close()
    return True
  if event == "-TS_TRAIN_MKO-":
    if bda_service.service.current_user.logged_in is False:
      return True
    model_name = values['-TS_MKO_NAME-']
    mko = bda_service.MKO(model_name, bt.user, bda_service.service, auto_progress=True)
    inputs = [str(ts.known_features[key]) for key in ts.inputs_keys]
    outputs = [str(ts.known_features[key]) for key in ts.outputs_keys]
    time_as_input = window["-TS_TIME_AS_INPUT-"].get()
    mko.set_inputs_and_outputs_ls(inputs, outputs, time_as_input)
    mko.set_time_parameters(
      ts.startTimeObj,
      ts.endTimeObj,
      values['-TS_SAMPLE_PERIOD-'],
      values['-TS_NUMBER_SAMPLES-']
    )
    mko.set_smip_auth(bt.smip_auth)
    add_mko_to_infer(mko, window)
    refresher.refresh_daemon.add_task(mko)
    return True

  ### LOT SERIES EVENTS SECTION ###
  if event == "-LS_INPUT_SEND-":
    avail_to_inputs(values, window, ls)
    return True
  if event == "-LS_RETURN_INPUT-":
    inputs_to_avail(values, window, ls)
    return True
  if event == "-LS_OUTPUT_SEND-":
    avail_to_outputs(values, window, ls)
    return True
  if event == "-LS_RETURN_OUTPUT-":
    outputs_to_avail(values, window, ls)
    return True
  if event == "-LS_SET_MAX_RANGE-":
    if values[event] == True:
      window['-LS_START_LOT-'].update(disabled=True)
      window['-LS_END_LOT-'].update(disabled=True)
      ls.all_lots = True
    else:
      window['-LS_START_LOT-'].update(disabled=False)
      window['-LS_END_LOT-'].update(disabled=False)
      ls.all_lots = False
  if event == "-LS_DOWNLOAD_REQUEST_FILENAME-":
    filename = values['-LS_DOWNLOAD_REQUEST_FILENAME-']
    df = get_lot_series(bt.smip_auth['url'],
      bt.smip_auth['token'], ls.feature_container_attrib,
      ls.all_lots,
      values['-LS_START_LOT-'],
      values['-LS_END_LOT-'],
    )
    df.dropna(inplace=True)
    df = df[ls.inputs_keys + ls.outputs_keys]
    with open(filename, "w") as fd:
      fd.write(df.to_csv(index=False))
      fd.close()
    return True
  if event == "-LS_TRAIN_MKO-":
    if bda_service.service.current_user.logged_in is False:
      return True
    model_name = values['-LS_MKO_NAME-']
    mko = bda_service.MKO(model_name, bt.user, bda_service.service, series_type="lot", auto_progress=True)
    inputs = [str(ls.known_features[key]) for key in ls.inputs_keys]
    outputs = [str(ls.known_features[key]) for key in ls.outputs_keys]
    mko.set_inputs_and_outputs_ls(ls.feature_container_attrib, inputs, outputs)
    mko.set_lot_parameters(
      ls.all_lots,
      values['-LS_START_LOT-'],
      values['-LS_END_LOT-']
    )
    mko.set_smip_auth(bt.smip_auth)
    add_mko_to_infer(mko, window)
    refresher.refresh_daemon.add_task(mko)
    return True



  return False