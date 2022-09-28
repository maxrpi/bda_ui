import PySimpleGUI as sg
import pandas as pd
import bda_service
import refresher
from bdaLogins.layout import layout
from footer import statusbar

class bs():
  settings = {}

def initialize(settings, window):
  assign_settings(settings, window)
  set_bindings(window)

def assign_settings(settings, window):
  bs.settings = settings
  if bs.settings['url'] is not None: window['-BDA_URL-'].update(bs.settings['url']) 
  if bs.settings['username'] is not None: window['-BDA_USER-'].update(bs.settings['username']) 
  if bs.settings['password'] is not None: window['-BDA_PASSWORD-'].update(bs.settings['password']) 
  if bs.settings['server_secret'] is not None: window['-SERVER_SECRET-'].update(bs.settings['server_secret']) 

def set_bindings(window):
  pass

def init_server(values):
  service_url = values["-BDA_URL-"]
  bs.settings['url'] = service_url
  secret = values["-SERVER_SECRET-"]
  bs.settings['server_secret'] = secret
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

def create_user(values) -> bda_service.User:
  username = values["-BDA_USER-"]
  password = values["-BDA_PASSWORD-"]
  bs.settings['username'] = username
  bs.settings['password'] = password
  user = bda_service.User(username, password)
  bda_service.service.add_user(user)
  return user


def handler(event, values, window):
  ### SERVICE EVENTS SECTION ###
  if event == "-INIT_SERVER-":
    try:
      init_server(values)
    except Exception as err:
      print(err)
    return True
  if event == "-CREATE_USER-":
    try:
      user = create_user(values)
      statusbar.update("User {user} created on BDA server")
    except Exception as err:
      print(err)
    return True

  if event == "-LOG_IN_BDA-":
    try:
      username = values["-BDA_USER-"]
      password = values["-BDA_PASSWORD-"]
      user = bda_service.User(username, password)
      if user == bda_service.service.current_user:
        user = bda_service.service.current_user
      bda_service.service.login_user(user)
      bda_service.service.set_current_user(user)
      refresher.refresh_daemon.add_task(user)
      window['-BDA_EXPIRES-'].update(user.auth_expiration)
      statusbar.update("logged {} in on BDA server".format(user.username))
    except Exception as err:
      statusbar.update("Could not login {} on server: {}".format(user.username, err))
    return True
  return False