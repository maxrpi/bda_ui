from nturl2path import url2pathname
import PySimpleGUI as sg
import requests

available_attribs = {"foo": 1}
inputs_list = []
outputs_list = []
top_text_width=16
bda_token_expiration = "no token"
smip_auth = {}
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
        [ sg.Listbox(values=list(available_attribs.keys()), size=(15,10,),
          enable_events=True, key="-ATTRIBUTE_LIST-", select_mode="LISTBOX_SELECT_MODE_SINGLE") ]
      ]
    ),
    sg.Column(
      [
        [ sg.B("INPUTS ->", enable_events=True, key="-INPUT_SEND-") ],
        [ sg.B("OUTPUT ->", enable_events=True, key="-OUTPUT_SEND-") ],
        [ sg.B("<- DELETE", enable_events=True, key="-DELETE_ATTRIB-") ]
      ],
      vertical_alignment="center"
    ),
    sg.Column(
      [
        [ sg.T("INPUTS") ],
        [ sg.Listbox(inputs_list, size=(15,8), select_mode="LISTBOX_SELECT_MODE_SINGLE",
            key="-INPUTS_LIST-")],
        [ sg.T("OUTPUT")],
        [ sg.Listbox(outputs_list, size=(15,3), select_mode="LISTBOX_SELECT_MODE_SINGLE",
            key="-OUTPUTS_LIST-")]
      ]
    ),
  ],
  [
    sg.Column(
      [
        [sg.T("Start Time"), sg.In("start time", size=(20, 1), key="-START_TIME-")],
        [sg.T("End Time"), sg.In("end time", size=(20, 1), key="-END_TIME-")],
        [sg.B("Set maximum range", enable_events=True, key="-SET_MAX_RANGE-")],
        [sg.T("Number of Samples"), sg.In("", size=(6,1), key="-NUMBER_SAMPLES-")]
      ]
    )
  ],
  [
    sg.T("Auth to send"),
    sg.Checkbox("SMIP token", key="-BOOL_SEND_TOKEN-"),
    sg.Checkbox("Username/Password", key="-BOOL_SEND_USERPASS-")
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

def add_attribute(attrib_id, attrib_name, window):
  print("received {} and {}".format(attrib_id, attrib_name))
  available_attribs[attrib_name] = attrib_id
  values = list(available_attribs.keys())
  print(values)
  window['-ATTRIBUTE_LIST-'].update(values=values)

def assign_settings(settings, window):
  if settings['url'] is not None: window['-BDA_URL-'].update(settings['url']) 
  if settings['username'] is not None: window['-BDA_USER-'].update(settings['username']) 
  if settings['password'] is not None: window['-BDA_PASSWORD-'].update(settings['password']) 

def set_smip_auth(url, username, role, password, token):
  global smip_auth
  smip_auth['url'] = url
  smip_auth['username'] = username
  smip_auth['role'] = role
  smip_auth['password'] = password
  smip_auth['token'] = token


def handler(event, values, window):
  if event == "-LOG_IN_BDA-":
    try:
      pass
    except Exception as err:
      print(err)
    return True
  return False

if __name__ == "__main__":
  sg.theme('Dark Amber')
  window = sg.Window('test', layout, font=('Helvetica', '14'))
  while True:
    event, values = window.read()
    
    handler(event, values, window)

    if event == sg.WINDOW_CLOSED:
      break

  window.close()
