import PySimpleGUI as sg
import jwt
import json
import datetime
from smip.graphQL import get_bearer_token, get_equipment_description

top_text_width=16
smip_token_expiration = "no token"
attrib_description = ""
url = ""
smip_token = ""

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
    sg.B("Send to BDA", enable_events=True, key="-SEND_TO_BDA"),
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
          sg.B("Upload file to tag", enable_events=True, key="-UPLOAD-"),
          sg.B("Download data from tag", enable_events=True, key="-DOWNLOADTAG-"),
        ],
        [
          sg.T("Tag name"), sg.In("TAGNAME", size=10, enable_events=True, key="-TAGNAME-"),
        ],
        [
          sg.B("Send tag to BDA", enable_events=True, key="-TAG_TO_BDA-")
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
  
def handler(event, values, window):
  global smip_token
  global url
  if event == "-GET_SMIP_TOKEN-":
    try:
      url = values['-SMIP_URL-']
      smip_token = get_bearer_token(url=url,
                    username=values['-SMIP_USER-'],
                    role=values['-SMIP_ROLE-'],
                    password=values['-SMIP_PASSWORD-']
      )
      unixexpiry= jwt.decode(smip_token, options={"verify_signature": False})['exp']
      print("got unixexpiry = {}".format(unixexpiry))
      smip_token_expiration = \
        datetime.datetime.fromtimestamp(unixexpiry).strftime("%m/%d/%Y, %H:%M:%S")
      window['-SMIP_EXPIRES-'].update(smip_token_expiration)
      print("Bearer {}".format(smip_token))
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
      window['-EP_DESCRIPTION-'].update("Could not validate tag {}".format(attrib_id))
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
