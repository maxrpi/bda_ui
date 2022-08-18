import PySimpleGUI as sg
import pandas as pd
import dateutil.parser
import datetime

known_attributes = {}
avail_keys = list(known_attributes.keys())
inputs_keys = []
outputs_keys = []
top_text_width=16
sorter_width = 30
bda_token_expiration = "no token"
smip_auth = {}
startTimeObj = None
endTimeObj = None
my_settings_copy = {}

layout = [
  [
    sg.T("BDA URL:"),
    sg.In("URL", enable_events=True, key="-BDA_URL-", size=32),
  ],
  [
    sg.T("BDA Username:"),
    sg.In("username", enable_events=True, key="-BDA_USER-", size=top_text_width),
    sg.T("BDA password:"),
    sg.In("password", enable_events=True, key="-BDA_PASSWORD-", size=top_text_width),
  ],
  [
    sg.B("Log in", enable_events=True, key="-LOG_IN_BDA-"),
    sg.T("BDA token expires:"),
    sg.Multiline(bda_token_expiration, size=(20,1),
                no_scrollbar=True, justification="t", key="-BDA_EXPIRES-"),
  ],
  [
    sg.HorizontalSeparator()
  ],
  [
    sg.T("CREATE ANALYSIS")
  ],
  [
    sg.Column(
      [
        [ sg.T("Available Attributes")],
        [ sg.Listbox(values=avail_keys, size=(sorter_width,15,),
            enable_events=True, key="-ATTRIBUTE_LIST-",
            select_mode="LISTBOX_SELECT_MODE_MULTIPLE") ]
      ]
    ),
    sg.Column(
      [
        [ sg.B("INPUTS ->", enable_events=True, key="-INPUT_SEND-") ],
        [ sg.B("<- INPUTS", enable_events=True, key="-RETURN_INPUT-") ],
        [ sg.HorizontalSeparator()],
        [ sg.B("OUTPUTS ->", enable_events=True, key="-OUTPUT_SEND-") ],
        [ sg.B("<- OUTPUTS", enable_events=True, key="-RETURN_OUTPUT-") ]
      ],
      vertical_alignment="center"
    ),
    sg.Column(
      [
        [ sg.T("INPUTS") ],
        [ sg.Listbox(inputs_keys, size=(sorter_width,8),
            select_mode="LISTBOX_SELECT_MODE_MULTIPLE",
            key="-INPUTS_LIST-")],
        [ sg.T("OUTPUT")],
        [ sg.Listbox(outputs_keys, size=(sorter_width,3),
            select_mode="LISTBOX_SELECT_MODE_MULTIPLE",
            key="-OUTPUTS_LIST-")]
      ]
    ),
  ],
  [
    sg.Column(
      [
        [ sg.T("Start Time"),
          sg.In("start time", size=(20, 1), key="-START_TIME-"),
          sg.B("Parse Start Time", enable_events=True, key="-PARSE_START-")
        ],
        [ sg.T("End Time"),
          sg.In("end time", size=(20, 1), key="-END_TIME-"),
          sg.B("Parse End Time", enable_events=True, key="-PARSE_END-")],
        [sg.B("Set maximum range", enable_events=True, key="-SET_MAX_RANGE-")],
        [sg.T("Number of Samples"), sg.In("0", size=(6,1), key="-NUMBER_SAMPLES-")],
        [sg.T("Sample period in seconds"), sg.In("0", size=(6,1), key="-SAMPLE_PERIOD-")]
      ]
    )
  ],
  [
    sg.T("Auth to send"),
    sg.Checkbox("SMIP token", key="-BOOL_SEND_TOKEN-"),
    sg.Checkbox("Username/Password", key="-BOOL_SEND_USERPASS-")
  ],
  [
    sg.In("", visible=False, enable_events=True, key="-DOWNLOAD_REQUEST_FILENAME-"),
    sg.SaveAs("Download Request Data",
      default_extension=".txt", file_types=[('Text','*.txt')],
      key='-DOWNLOAD_REQUEST_DATA-',
      enable_events=True)
  ],
  [
    sg.T("Name for MKO"),
    sg.In("name", key="-MKOname-"),
    sg.B("Request MKO training", enable_events=True, key="-TRAIN_MKO-")
  ],
  [
    sg.T("Error Output", visible=False, key="-ERRORREPORT1-"),
    sg.Multiline("Error Output", visible=False, key="-ERRORREPORT2-")
  ] 
]

def assign_settings(settings, window):
  global my_settings_copy
  my_settings_copy = settings
  if settings['url'] is not None: window['-BDA_URL-'].update(settings['url']) 
  if settings['username'] is not None: window['-BDA_USER-'].update(settings['username']) 
  if settings['password'] is not None: window['-BDA_PASSWORD-'].update(settings['password']) 

def set_bindings(window):
  window['-PARSE_START-'].bind('<KeyPress-Return>','RETURN')
  window['-PARSE_END-'].bind('<KeyPress-Return>','RETURN')

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
  selected_keys = values['-ATTRIBUTE_LIST-']
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
  window[key].update(value=dateObj.strftime("%Y-%m-%dT%H:%M:%SZ"))
  return dateObj
  
def create_attrib_id_list():
  global known_attributes, inputs_keys, outputs_keys
  attrib_id_list = [known_attributes[key] for key in inputs_keys + outputs_keys]
  attrib_id_list_string = ",".join(attrib_id_list)
  print("attrib_id_list:", attrib_id_list_string)
  return attrib_id_list

def handler(event, values, window, get_timeseries_array):
  global startTimeObj, endTimeObj
  if event == "-LOG_IN_BDA-":
    try:
      pass
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
    return True
  if event == "-PARSE_END-" or event == "END_TIME" + "RETURN":
    key = "-END_TIME-"
    endTimeObj = parseTime(key, values[key], window)
    return True
  if event == "-SET_MAX_RANGE-":
    startTimeObj = parseTime("-START_TIME-", "1900-01-01", window)
    endTimeObj = parseTime("-END_TIME-", "2100-01-01", window)
    return True

  if event == "-DOWNLOAD_REQUEST_FILENAME-":
    print("got event:", event)
    filename = values['-DOWNLOAD_REQUEST_FILENAME-']
    df = get_timeseries_array(smip_auth['url'],
      smip_auth['token'], create_attrib_id_list(),
      startTimeObj.strftime("%Y-%m-%d %H:%M:%S+00"),
      endTimeObj.strftime("%Y-%m-%d %H:%M:%S+00"),
      values['-NUMBER_SAMPLES-'],
      datetime.timedelta(seconds=int(values['-SAMPLE_PERIOD-'])))
    
    with open(filename, "w") as fd:
      fd.write(df.to_csv(index=False, date_format="%Y-%m-%d %H:%M:%S+00"))
      fd.close()
      
    return True
  return False

if __name__ == "__main__":
  sg.theme('Dark Amber')
  window = sg.Window('test', layout, font=('Helvetica', '14'))
  while True:
    event, values = window.read()
    
    handler(event, values, window, None)

    if event == sg.WINDOW_CLOSED:
      break

  window.close()
