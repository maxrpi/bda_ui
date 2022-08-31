import PySimpleGUI as sg
from datetime import datetime


layout = [[
  sg.Exit(key="-EXIT-"),
  sg.B("Save state", enable_events=True, key="-SAVE_STATE-"),
  sg.B("Load state", enable_events=True, key="-LOAD_STATE-"),
  sg.T("", expand_x=True, key="-STATUS_BAR-")
]]

class StatusBar(object):
  def __init__(self, key) -> None:
    self._key = key   

  def register_statusbar(self, window):
    self._window = window

  def update(self, message):
    smalldate = datetime.now().strftime("%H:%M:%S")
    self._window['-STATUS_BAR-'].update("{} - {}".format(smalldate, message))

statusbar = StatusBar(key="-STATUS_BAR-")

def handler(event, values, window):
    if event == sg.WINDOW_CLOSED or event == "-EXIT-":
      window.close()