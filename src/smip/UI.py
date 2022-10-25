import PySimpleGUI as sg
import jwt
import json
import datetime
import smip.graphQL
import pyperclip
from  smip.layout import layout, SetLED
from footer import statusbar

class sm():
  smip_token_expiration = "no token"
  attrib_description = ""
  url = ""
  smip_token = None
  username = ""
  password = ""
  role = ""
  attrib_id = None
  data_type = ""
  settings = {}


def initialize(settings, window):
  assign_settings(settings, window)
  set_bindings(window)

def assign_settings(settings, window):
  sm.settings = settings
  if settings['url'] is not None: window['-SMIP_URL-'].update(settings['url']) 
  if settings['username'] is not None: window['-SMIP_USER-'].update(settings['username']) 
  if settings['role'] is not None: window['-SMIP_ROLE-'].update(settings['role']) 
  if settings['password'] is not None: window['-SMIP_PASSWORD-'].update(settings['password']) 
  if settings['attribute_id'] is not None: window['-ATTRIBUTE_ID-'].update(settings['attribute_id']) 
  
def set_bindings(window):
  window['-ATTRIBUTE_NAME-'].bind('<KeyPress-Return>','RETURN')
  window['-SMIP_PASSWORD-'].bind('<KeyPress-Return>','RETURN')




def handler(event, values, window, token_to_BDA, ts_to_BDA, ls_to_BDA):

  if event == "-GET_SMIP_TOKEN-" or event == "-SMIP_PASSWORD-" + "RETURN":
    try:
      sm.url = values['-SMIP_URL-']
      sm.username=values['-SMIP_USER-']
      sm.role=values['-SMIP_ROLE-']
      sm.password=values['-SMIP_PASSWORD-']

      sm.smip_token = smip.graphQL.get_bearer_token(url=sm.url, username=sm.username,
                    role=sm.role, password=sm.password
      )
      sm.smip_token_expiration = \
        datetime.datetime.fromtimestamp(
          jwt.decode(sm.smip_token, options={"verify_signature": False})['exp']
        ).strftime("%m/%d/%Y, %H:%M:%S")

      window['-SMIP_EXPIRES-'].update(sm.smip_token_expiration)
      window['-SEND_TO_CLIPBOARD-'].update(visible=True)
      token_to_BDA(sm.url, sm.username, sm.role, sm.password, sm.smip_token)
      statusbar.update("TOKEN SENT TO BDA SIDE")
    except Exception as err:
      print(err)
    return True

  if event == "-VALIDATE_ID-":
    try:
      sm.attrib_id = values['-ATTRIBUTE_ID-']
      sm.attrib_description = smip.graphQL.get_equipment_description(sm.url, sm.smip_token, sm.attrib_id)
      displayName = sm.attrib_description['attribute']['displayName']
      sm.data_type = sm.attrib_description['attribute']['dataType']
      if sm.data_type == "OBJECT":
        SetLED(window, "-LOT_LED-", "yellow")
        SetLED(window, "-TIMESERIES_LED-", "gray")
      else:
        SetLED(window, "-LOT_LED-", "gray")
        SetLED(window, "-TIMESERIES_LED-", "yellow")
      pretty_attrib = json.dumps(sm.attrib_description, sort_keys=True, indent=2)
      window['-EP_DESCRIPTION-'].update(f"{sm.attrib_id}: {pretty_attrib}")
      window['-ATTRIBUTE_NAME-'].update("{}_{}".format(displayName,sm.attrib_id))
      window["-DELETE_DATA_FROM_ID-"].update(visible=True)
      window["-DOWNLOAD_ATTRIBUTE-"].update(visible=True)

      sm.settings['attribute_id'] = sm.attrib_id
    except Exception as err:
      window['-EP_DESCRIPTION-'].update("Could not validate id {}".format(sm.attrib_id))
    return True

  if event == "-DELETE_DATA_FROM_ID-":
    try:
      sm.attrib_id = values['-ATTRIBUTE_ID-']
      sm.attrib_description = smip.graphQL.get_equipment_description(sm.url, sm.smip_token, sm.attrib_id)
      displayName = sm.attrib_description['attribute']['displayName']
      confirm_message = "Please confirm IRREVERSIBLE deletion of data from\n   \
        Attribute with ID: {} and name {}:".format(sm.attrib_id, displayName)
      user_confirmed = sg.PopupOKCancel(confirm_message, title="DELETION ALERT", button_color=("red","blue"))
      if user_confirmed == "OK":
        smip.graphQL.delete_timeseries_id(sm.url, sm.smip_token, sm.attrib_id)
        window["-DELETE_DATA_FROM_ID-"].update(visible=False)
        sm.settings['attribute_id'] = ""
    except Exception as err:
      sg.Popup("Attribute {} data NOT deleted.".format(sm.attrib_id), auto_close=False)
    return True

  if event == "-UPLOAD_FILENAME-":
    try:
      sm.attrib_id = values['-ATTRIBUTE_ID-']
      if values['-REPLACE_ALL-'] == True: replace_all = True 
      else: replace_all = False

      if sm.data_type == "OBJECT":
        smip.graphQL.post_lot_series_id(sm.url, sm.smip_token, sm.attrib_id,
          filename = values["-UPLOAD_FILENAME-"], replace_all=replace_all)
      else:
        print(smip.graphQL.post_timeseries_id(sm.url, sm.smip_token, sm.attrib_id,
          filename = values['-UPLOAD_FILENAME-'], replace_all=replace_all))
    except Exception as err:
      print(err)
    return True

  if event == "-DOWNLOAD_ATTRIBUTE-":
      window["-DOWNLOAD_ATTRIBUTE-"].update(visible=True)
      if sm.data_type == "OBJECT":
        attrib_data = smip.graphQL.get_lot_series(sm.url, sm.smip_token, sm.attrib_id).to_csv(index=False)
      else:
        attrib_data = smip.graphQL.get_raw_attribute_data(sm.url, sm.smip_token, sm.attrib_id, strip_nan=True)
      window['-EP_DESCRIPTION-'].update(attrib_data)
      return True

  if event == "-ATTRIBUTE_TO_BDA-" or event == "-ATTRIBUTE_NAME-" + "RETURN":
    try:
      attrib_name = values['-ATTRIBUTE_NAME-']
      sm.attrib_id = values['-ATTRIBUTE_ID-']
      sm.attrib_description = smip.graphQL.get_equipment_description(sm.url, sm.smip_token, sm.attrib_id)
      sm.data_type = sm.attrib_description['attribute']['dataType']
      if sm.data_type == "OBJECT":
        df = smip.graphQL.get_lot_series(sm.url, sm.smip_token, sm.attrib_id)
        feature_list = df.columns.tolist()
        ls_to_BDA(sm.attrib_id, attrib_name, feature_list, window)
      else:
        ts_to_BDA(sm.attrib_id,attrib_name, window)
      window['-ATTRIBUTE_NAME-'].update(select=True)
      statusbar.update("Send attrib {} to bda tab with name {}".
        format(values['-ATTRIBUTE_ID-'], values['-ATTRIBUTE_NAME-']) )
    except Exception as err:
      statusbar.update("Couldn't send attrib {} to bda tab".
        format(values['-ATTRIBUTE_ID-']) )
      print(err)
    return True

  if event == "-SEND_TO_BDA-":
    try:
      token_to_BDA(sm.url, sm.username, sm.role, sm.password, sm.smip_token)
      statusbar.update("TOKEN SENT TO BDA SIDE")
    except Exception as err:
      print(err)
    return True

  if event == "-SEND_TO_CLIPBOARD-":
    try:
      pyperclip.copy(sm.smip_token)
      statusbar.update("TOKEN COPIED TO CLIPBOARD")
    except Exception as err:
      print(err)
    return True



  return False


if __name__ == "__main__":
  sg.theme('Dark Amber')
  window = sg.Window('test', layout, font=('Helvetica', '14'))
  while True:
    event, values = window.read()
    
    handler(event, values, window, None, None, None)

    if event == sg.WINDOW_CLOSED:
      break

  window.close()
