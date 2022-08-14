from lib2to3.pgen2 import token
import PySimpleGUI as sg
import jwt
import json
import datetime
from smip.graphQL import get_bearer_token, get_equipment_description, post_timeseries_id
top_text_width=16
smip_token_expiration = "no token"
attrib_description = ""
url = ""
smip_token = None
username = ""
password = ""
role = ""
attrib_id = None

layout = [
  [
    sg.T("URL:"),
    sg.In(url, enable_events=True, key="-SMIP_URL-", size=32),
  ],
  [
    sg.T("SMIP Username:"),
    sg.In("username", enable_events=True, key="-SMIP_USER-", size=top_text_width),
    sg.T("SMIP role:"),
    sg.In("role", enable_events=True, key="-SMIP_ROLE-", size=top_text_width),
    sg.T("SMIP password:"),
    sg.In("password", enable_events=True, key="-SMIP_PASSWORD-", size=top_text_width),
  ],
  [
    sg.B("Get Token", enable_events=True, key="-GET_SMIP_TOKEN-"),
    sg.B("Send to BDA", enable_events=True, visible=False, key="-SEND_TO_BDA-"),
    sg.T("SMIP token expires:"),
    sg.Multiline(smip_token_expiration, size=(20,1),
                no_scrollbar=True, justification="t", key="-SMIP_EXPIRES-"),
  ],
  [
    sg.HorizontalSeparator()
  ],
  [
    sg.Column(
      [
        [
          sg.T("Attribute id:"),
          sg.In("", size=(5, 1), key="-ATTRIBUTE_ID-"),
        ],
        [
          sg.B("Validate Id", enable_events=True, key="-VALIDATE_ID-")
        ],
        [
          sg.In("", visible=False, key='-UPLOAD_FILENAME-', enable_events=True),
          sg.FileBrowse("Upload file to attribute", enable_events=True, target="-UPLOAD_FILENAME-"),
          sg.B("Download data from attribute", enable_events=True, key="-DOWNLOAD_ATTRIBUTE-"),
        ],
        [
          sg.T("Attribute name"), sg.In("ATTRIBUTE NAME", size=10, enable_events=True, key="-ATTRIBUTE_NAME-"),
        ],
        [
          sg.B("Send attribute to BDA", enable_events=True, key="-ATTRIBUTE_TO_BDA-")
        ]
      ],
      vertical_alignment='top', justification='l', p=10
    ),
    sg.Column(
      [
        [
          sg.T("Eq/Prop Description"),
        ],
        [
          sg.Multiline(attrib_description,size=(40,30), key="-EP_DESCRIPTION-")
        ]
      ],
      element_justification='l',justification='l'
    ),
  ],
]

def assign_settings(settings, window):
  if settings['url'] is not None: window['-SMIP_URL-'].update(settings['url']) 
  if settings['username'] is not None: window['-SMIP_USER-'].update(settings['username']) 
  if settings['role'] is not None: window['-SMIP_ROLE-'].update(settings['role']) 
  if settings['password'] is not None: window['-SMIP_PASSWORD-'].update(settings['password']) 
  
def handler(event, values, window, token_to_BDA, attrib_to_BDA):
  global smip_token
  global url
  global username
  global role
  global password
  global attrib_id
  if event == "-GET_SMIP_TOKEN-":
    try:
      url = values['-SMIP_URL-']
      username=values['-SMIP_USER-']
      role=values['-SMIP_ROLE-']
      password=values['-SMIP_PASSWORD-']

      smip_token = get_bearer_token(url=url,
                    username=username,
                    role=role,
                    password=password
      )
      unixexpiry= jwt.decode(smip_token, options={"verify_signature": False})['exp']
      print("got unixexpiry = {}".format(unixexpiry))
      smip_token_expiration = \
        datetime.datetime.fromtimestamp(unixexpiry).strftime("%m/%d/%Y, %H:%M:%S")
      window['-SMIP_EXPIRES-'].update(smip_token_expiration)
      print("Bearer {}".format(smip_token))
      window['-SEND_TO_BDA-'].update(visible=True)
    except Exception as err:
      print(err)
    return True

  if event == "-VALIDATE_ID-":
    try:
      attrib_id = values['-ATTRIBUTE_ID-']
      attrib_description = get_equipment_description(url, smip_token, attrib_id)
      pretty_attrib = json.dumps(attrib_description, sort_keys=True, indent=2)
      window['-EP_DESCRIPTION-'].update(f"{attrib_id}: {pretty_attrib}")
    except Exception as err:
      print("err: {}".format(err))
      window['-EP_DESCRIPTION-'].update("Could not validate id {}".format(attrib_id))
    return True

  if event == "-UPLOAD_FILENAME-":
    try:
      attrib_id = values['-ATTRIBUTE_ID-']
      post_timeseries_id(url, smip_token, attrib_id, filename = values['-UPLOAD_FILENAME-'])
    except Exception as err:
      print(err)
    return True

  if event == "-ATTRIBUTE_TO_BDA-":
    try:
      attrib_to_BDA(values['-ATTRIBUTE_ID-'], values['-ATTRIBUTE_NAME-'], window)
    except Exception as err:
      print(err)
    return True

  if event == "-SEND_TO_BDA-":
    try:
      print("attempting to send auth to BDA")
      token_to_BDA(url, username, role, password, smip_token)
    except Exception as err:
      print(err)
    return True


  return False




if __name__ == "__main__":
  sg.theme('Dark Amber')
  window = sg.Window('test', layout, font=('Helvetica', '14'))
  while True:
    event, values = window.read()
    
    handler(event, values, window, None, None)

    if event == sg.WINDOW_CLOSED:
      break

  window.close()
