import PySimpleGUI as sg
import jwt
import json
import datetime
import smip.graphQL
top_text_width=16
smip_token_expiration = "no token"
attrib_description = ""
url = ""
smip_token = None
username = ""
password = ""
role = ""
attrib_id = None
my_settings_copy = {}

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
    sg.In("password", enable_events=True, key="-SMIP_PASSWORD-", size=top_text_width,
      password_char="*"),
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
          sg.B("Validate Id", enable_events=True, key="-VALIDATE_ID-"),
          sg.B("Delete all data from ID", button_color="red", enable_events=True, visible=False, key="-DELETE_DATA_FROM_ID-")
        ],
        [
          sg.In("", visible=False, key='-UPLOAD_FILENAME-', enable_events=True),
          sg.FileBrowse("Upload file to attribute", enable_events=True, target="-UPLOAD_FILENAME-"),
        ],
        [
          sg.Radio("Replace All", group_id="InsertReplace", default=True, key="-REPLACE_ALL-" ),
          sg.Radio("Insert", group_id="InsertReplace", default=False, key="-INSERT_DATA-" )
        ],
        [
          sg.B("Download attribute data", enable_events=True, key="-DOWNLOAD_ATTRIBUTE-", visible=False)
        ],
        [
          sg.T("Attribute name"), 
        ],
        [
          sg.In("ATTRIBUTE NAME", size=30, enable_events=True, key="-ATTRIBUTE_NAME-") 
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
  global my_settings_copy
  my_settings_copy = settings
  if settings['url'] is not None: window['-SMIP_URL-'].update(settings['url']) 
  if settings['username'] is not None: window['-SMIP_USER-'].update(settings['username']) 
  if settings['role'] is not None: window['-SMIP_ROLE-'].update(settings['role']) 
  if settings['password'] is not None: window['-SMIP_PASSWORD-'].update(settings['password']) 
  if settings['attribute_id'] is not None: window['-ATTRIBUTE_ID-'].update(settings['attribute_id']) 
  
def set_bindings(window):
  window['-ATTRIBUTE_NAME-'].bind('<KeyPress-Return>','RETURN')
  window['-SMIP_PASSWORD-'].bind('<KeyPress-Return>','RETURN')




def handler(event, values, window, token_to_BDA, attrib_to_BDA):

  global smip_token, url, username, role, password, attrib_id, my_settings_copy
  if event == "-GET_SMIP_TOKEN-" or event == "-SMIP_PASSWORD-" + "RETURN":
    try:
      url = values['-SMIP_URL-']
      username=values['-SMIP_USER-']
      role=values['-SMIP_ROLE-']
      password=values['-SMIP_PASSWORD-']

      smip_token = smip.graphQL.get_bearer_token(url=url, username=username,
                    role=role, password=password
      )
      smip_token_expiration = \
        datetime.datetime.fromtimestamp(
          jwt.decode(smip_token, options={"verify_signature": False})['exp']
        ).strftime("%m/%d/%Y, %H:%M:%S")

      window['-SMIP_EXPIRES-'].update(smip_token_expiration)
      window['-SEND_TO_BDA-'].update(visible=True)
    except Exception as err:
      print(err)
    return True

  if event == "-VALIDATE_ID-":
    try:
      attrib_id = values['-ATTRIBUTE_ID-']
      attrib_description = smip.graphQL.get_equipment_description(url, smip_token, attrib_id)
      displayName = attrib_description['attribute']['displayName']
      pretty_attrib = json.dumps(attrib_description, sort_keys=True, indent=2)
      window['-EP_DESCRIPTION-'].update(f"{attrib_id}: {pretty_attrib}")
      window['-ATTRIBUTE_NAME-'].update("{}_{}".format(displayName,attrib_id))
      window["-DELETE_DATA_FROM_ID-"].update(visible=True)
      window["-DOWNLOAD_ATTRIBUTE-"].update(visible=True)
      my_settings_copy['attribute_id'] = attrib_id
    except Exception as err:
      window['-EP_DESCRIPTION-'].update("Could not validate id {}".format(attrib_id))
    return True

  if event == "-DELETE_DATA_FROM_ID-":
    try:
      attrib_id = values['-ATTRIBUTE_ID-']
      attrib_description = smip.graphQL.get_equipment_description(url, smip_token, attrib_id)
      displayName = attrib_description['attribute']['displayName']
      confirm_message = "Please confirm IRREVERSIBLE deletion of data from\n   \
        Attribute with ID: {} and name {}:".format(attrib_id, displayName)
      user_confirmed = sg.PopupOKCancel(confirm_message, title="DELETION ALERT", button_color=("red","blue"))
      if user_confirmed == "OK":
        smip.graphQL.delete_timeseries_id(url, smip_token, attrib_id)
        window["-DELETE_DATA_FROM_ID-"].update(visible=False)
        my_settings_copy['attribute_id'] = ""
    except Exception as err:
      sg.Popup("Attribute {} data NOT deleted.".format(attrib_id), auto_close=False)
    return True

  if event == "-UPLOAD_FILENAME-":
    try:
      attrib_id = values['-ATTRIBUTE_ID-']
      if values['-REPLACE_ALL-'] == True: replace_all = True 
      else: replace_all = False

      print(smip.graphQL.post_timeseries_id(url, smip_token, attrib_id,
        filename = values['-UPLOAD_FILENAME-'], replace_all=replace_all))
    except Exception as err:
      print(err)
    return True

  if event == "-DOWNLOAD_ATTRIBUTE-":
      window["-DOWNLOAD_ATTRIBUTE-"].update(visible=True)
      attrib_data = smip.graphQL.get_raw_attribute_data(url, smip_token, attrib_id)
      window['-EP_DESCRIPTION-'].update(attrib_data)
      return True

  if event == "-ATTRIBUTE_TO_BDA-" or event == "-ATTRIBUTE_NAME-" + "RETURN":
    try:
      attrib_to_BDA(values['-ATTRIBUTE_ID-'], values['-ATTRIBUTE_NAME-'], window)
      window['-ATTRIBUTE_NAME-'].update(select=True)
    except Exception as err:
      print(err)
    return True

  if event == "-SEND_TO_BDA-":
    try:
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
