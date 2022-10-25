import PySimpleGUI as sg
import pandas as pd
import dateutil.parser
import datetime
from pathlib import Path
import bda_service
import refresher
from bdaData.layout import layout, timeseries_tab, lot_series_tab
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
class bd():
  current_tab = "-TIMESERIES_TAB-"
  smip_auth = {}
  settings = {}

  known_mkos = {}
  ready_mkos = []
  pending_mkos = []
  pending_mko_table = refresher.Element()
  mko_progress_bars = {}
  filecounter = 0
  

def initialize(settings, window):
  set_current_tab(window, bd.current_tab)
  assign_settings(settings, window)
  set_bindings(window)

def set_current_tab(window, tab_name):
  try:
    bd.current_tab = tab_name
    window[bd.current_tab].select()
  except KeyError as err:
    print(f"No such tab as {tab_name}")

def assign_settings(my_settings, window):
  bd.settings = my_settings
  if bd.settings['start_time'] is not None: window['-TS_START_TIME-'].update(bd.settings['start_time']) 
  if bd.settings['end_time'] is not None: window['-TS_END_TIME-'].update(bd.settings['end_time']) 
  if bd.settings['sample_period'] is not None: window['-TS_SAMPLE_PERIOD-'].update(bd.settings['sample_period']) 
  if bd.settings['number_samples'] is not None: window['-TS_NUMBER_SAMPLES-'].update(bd.settings['number_samples']) 

def set_bindings(window):
  window['-TS_PARSE_START-'].bind('<KeyPress-Return>','RETURN')
  window['-TS_PARSE_END-'].bind('<KeyPress-Return>','RETURN')
  window['-TS_SAMPLE_PERIOD-'].bind('<KeyPress-Return>','RETURN')
  window['-TS_NUMBER_SAMPLES-'].bind('<KeyPress-Return>','RETURN')

def set_smip_auth(url, username, role, password, token):
  bd.smip_auth['url'] = url
  bd.smip_auth['username'] = username
  bd.smip_auth['role'] = role
  bd.smip_auth['password'] = password
  bd.smip_auth['token'] = token

def add_timeseries(attrib_id, attrib_name, window):
  
  if attrib_name not in ts.known_features:
    ts.avail_keys.append(attrib_name)
    ts.known_features[attrib_name] = attrib_id
    window['-TS_FEATURE_LIST-'].update(values=ts.avail_keys)
    new_index = ts.avail_keys.index(attrib_name)
    window['-TS_FEATURE_LIST-'].update(set_to_index=[new_index],
      scroll_to_index=new_index)
    timeseries_tab.select()
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
  lot_series_tab.select()

def avail_to_inputs(values, window, tab):
  selected_indexes = window[f'-{tab.prefix}_FEATURE_LIST-'].get_indexes()
  moving = [tab.avail_keys[index] for index in selected_indexes]
  for item in moving:
    tab.avail_keys.remove(item)
    tab.inputs_keys.append(item)
  window[f'-{tab.prefix}_FEATURE_LIST-'].update(tab.avail_keys)
  window[f'-{tab.prefix}_INPUTS_LIST-'].update(tab.inputs_keys)

def avail_to_outputs(values, window, tab):
  selected_indexes = window[f'-{tab.prefix}_FEATURE_LIST-'].get_indexes()
  moving = [tab.avail_keys[index] for index in selected_indexes]
  for item in moving:
    tab.avail_keys.remove(item)
    tab.outputs_keys.append(item)
  window[f'-{tab.prefix}_FEATURE_LIST-'].update(tab.avail_keys)
  window[f'-{tab.prefix}_OUTPUTS_LIST-'].update(tab.outputs_keys)

def inputs_to_avail(values, window, tab):
  selected_indexes = window[f'-{tab.prefix}_INPUTS_LIST-'].get_indexes()
  moving = [tab.inputs_keys[index] for index in selected_indexes]
  for item in moving:
    tab.inputs_keys.remove(item)
    tab.avail_keys.append(item)
  window[f'-{tab.prefix}_INPUTS_LIST-'].update(tab.inputs_keys)
  window[f'-{tab.prefix}_FEATURE_LIST-'].update(tab.avail_keys)

def outputs_to_avail(values, window, tab):
  selected_indexes = window[f'-{tab.prefix}_OUTPUTS_LIST-'].get_indexes()
  moving = [tab.outputs_keys[index] for index in selected_indexes]
  for item in moving:
    tab.outputs_keys.remove(item)
    tab.avail_keys.append(item)
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

def ts_create_mko(model_name, values):
    if bda_service.service.current_user.logged_in is False:
      return True
    mko = bda_service.MKO(model_name,
      bda_service.service.current_user,
      bda_service.service,
      series_type="time",
      auto_progress=False
      )
    inputs = [str(ts.known_features[key]) for key in ts.inputs_keys]
    outputs = [str(ts.known_features[key]) for key in ts.outputs_keys]
    time_as_input = values["-TS_TIME_AS_INPUT-"]
    mko.set_inputs_and_outputs_ts(inputs, outputs, time_as_input)
    mko.set_time_parameters(
      ts.startTimeObj,
      ts.endTimeObj,
      values['-TS_SAMPLE_PERIOD-'],
      values['-TS_NUMBER_SAMPLES-']
    )
    mko.set_smip_auth(bda_service.service.smip_auth)
    return mko

def ls_create_mko(model_name, values):
  if bda_service.service.current_user.logged_in is False:
    return True
  mko = bda_service.MKO(model_name,
    bda_service.service.current_user,
    bda_service.service,
    series_type="lot",
    auto_progress=False
    )
  mko.set_inputs_and_outputs_ls(
    ls.feature_container_attrib,
    ls.inputs_keys,
    ls.outputs_keys
  )
  mko.set_lot_parameters(
    ls.all_lots,
    values['-LS_START_LOT-'],
    values['-LS_END_LOT-']
  )
  mko.set_smip_auth(bda_service.service.smip_auth)
  return mko

def ts_create_request_as_dataframe(values, get_timeseries_array):
  df = get_timeseries_array(bda_service.service.smip_auth['url'],
    bda_service.service.smip_auth['token'], create_feature_id_list_ts(ts),
    ts.startTimeObj.strftime("%Y-%m-%d %H:%M:%S+00"),
    ts.endTimeObj.strftime("%Y-%m-%d %H:%M:%S+00"),
    values['-TS_NUMBER_SAMPLES-'],
    datetime.timedelta(seconds=int(float(values['-TS_SAMPLE_PERIOD-']))))
  time_as_timestamp = values['-TS_TIME_AS_TIMESTAMP-']
  df.dropna(inplace=True)
  if time_as_timestamp:
    df['ts'] = pd.to_datetime(df.ts)
    df['ts'] = df.ts.astype('int64') //  10**9
  return df

def ls_create_request_as_dataframe(values, get_lot_series):
  df = get_lot_series(bda_service.service.smip_auth['url'],
    bda_service.service.smip_auth['token'], ls.feature_container_attrib,
    ls.all_lots,
    values['-LS_START_LOT-'],
    values['-LS_END_LOT-'],
  )
  df.dropna(inplace=True)
  df = df[ls.inputs_keys + ls.outputs_keys]
  return df

def handler(event, values, window, get_timeseries_array, get_lot_series, add_mko_to_train):

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
  if event == "-TS_PARSE_START-" or event == "-TS_START_TIME-" + "RETURN":
    key = "-TS_START_TIME-"
    ts.startTimeObj = parseTime(key, values[key], window)
    bd.settings["start_time"] = values[key]
    s, p = samples_and_periods(values['-TS_NUMBER_SAMPLES-'], values['-TS_SAMPLE_PERIOD-'])
    window['-TS_NUMBER_SAMPLES-'].update(str(s))
    window['-TS_SAMPLE_PERIOD-'].update(str(p))
    bd.settings['number_samples'] = s
    bd.settings['period'] = p
    return True
  if event == "-TS_PARSE_END-" or event == "-TS_END_TIME-" + "RETURN":
    key = "-TS_END_TIME-"
    ts.endTimeObj = parseTime(key, values[key], window)
    bd.settings["end_time"] = values[key]
    s, p = samples_and_periods(values['-TS_NUMBER_SAMPLES-'], values['-TS_SAMPLE_PERIOD-'])
    window['-TS_NUMBER_SAMPLES-'].update(str(s))
    window['-TS_SAMPLE_PERIOD-'].update(str(p))
    bd.settings['number_samples'] = s
    bd.settings['period'] = p
    return True
  if event == "-TS_SET_MAX_RANGE-":
    ts.startTimeObj = parseTime("-TS_START_TIME-", "1900-01-01", window)
    ts.endTimeObj = parseTime("-TS_END_TIME-", "2100-01-01", window)
    s, p = samples_and_periods(values['-TS_NUMBER_SAMPLES-'], values['-TS_SAMPLE_PERIOD-'])
    window['-TS_NUMBER_SAMPLES-'].update(str(s))
    window['-TS_SAMPLE_PERIOD-'].update(str(p))
    bd.settings['number_samples'] = s
    bd.settings['period'] = p
    return True
  if event == "-TS_NUMBER_SAMPLES-" + "RETURN":
    s, p = samples_and_periods(values['-TS_NUMBER_SAMPLES-'], values['-TS_SAMPLE_PERIOD-'], priority="s")
    window['-TS_NUMBER_SAMPLES-'].update(str(s))
    window['-TS_SAMPLE_PERIOD-'].update(str(p))
    bd.settings['number_samples'] = s
    bd.settings['period'] = p
    return True
  if event == "-TS_SAMPLE_PERIOD-" + "RETURN":
    s, p = samples_and_periods(values['-TS_NUMBER_SAMPLES-'], values['-TS_SAMPLE_PERIOD-'], priority="p")
    window['-TS_NUMBER_SAMPLES-'].update(str(s))
    window['-TS_SAMPLE_PERIOD-'].update(str(p))
    bd.settings['number_samples'] = s
    bd.settings['period'] = p
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

  #### NON-TAB SPECIFIC, MKO FUNCTIONS ####
  if event == "-DS_DOWNLOAD_REQUEST_FILENAME-":
    filename = values['-DS_DOWNLOAD_REQUEST_FILENAME-']
    tab = window['-DATASPEC_TABGR-'].get().upper()
    if tab == '-LOT_SERIES_TAB-':
      df = ls_create_request_as_dataframe(values, get_lot_series)
      tabname = "lot series"
    elif tab == "-TIMESERIES_TAB-":
      df = ts_create_request_as_dataframe(values, get_timeseries_array)
      tabname = "time series"
    else:
      raise Exception("This can't happen")
    with open(filename, "w") as fd:
      fd.write(df.to_csv(index=False, date_format="%Y-%m-%d %H:%M:%S+00"))
      fd.close()
    statusbar.update(f"Downloaded {tabname} to file {filename}")
    return True
    
  if event == "-DS_SEND_MKO_TO_TRAINING-":
    model_name = values['-DS_MKO_NAME-']
    tab = window['-DATASPEC_TABGR-'].get().upper()
    if tab == '-LOT_SERIES_TAB-':
      mko = ls_create_mko(model_name, values)
      tabname = "lot series"
    elif tab == "-TIMESERIES_TAB-":
      mko = ts_create_mko(model_name, values)
      tabname = "timeseries"
    else:
      raise Exception("This can't happen")
    add_mko_to_train(mko, window) 
    statusbar.update(f"Sent '{model_name}' ({tabname} mko) to ondeck")
    return True

  return False