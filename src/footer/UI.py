import PySimpleGUI as sg
from datetime import datetime
from time import sleep

def LEDIndicator(key=None, radius=30):
    return sg.Graph(canvas_size=(radius, radius),
             graph_bottom_left=(-radius, -radius),
             graph_top_right=(radius, radius),
             pad=(0, 0), key=key)

def SetLED(window, key, color):
    graph = window[key]
    graph.erase()
    graph.draw_circle((0, 0), 12, fill_color=color, line_color=color)

layout = [[
  sg.Exit(key="-EXIT-"),
  LEDIndicator("-HEARTBEAT-"),
  #sg.B("Save state", enable_events=True, key="-SAVE_STATE-"),
  #sg.B("Load state", enable_events=True, key="-LOAD_STATE-"),
  sg.Multiline("", size=(40,2), expand_x=True, key="-STATUS_BAR-")
]]

class StatusBar(object):
  def __init__(self, key) -> None:
    self._key = key   
    self._registered = False

  def register_statusbar(self, window):
    self._window = window
    self._registered = True

  def update(self, message):
    smalldate = datetime.now().strftime("%H:%M:%S")
    self._window['-STATUS_BAR-'].update("{} - {}".format(smalldate, message),
    text_color="black", background_color="white")

  def error(self, message):
    smalldate = datetime.now().strftime("%H:%M:%S")
    self._window['-STATUS_BAR-'].update("{} - {}".format(smalldate, message),
    text_color="white", background_color="red")
  
  def pulse(self):
    if self._registered:
      SetLED(self._window, '-HEARTBEAT-', "green")
      sleep(0.4)
      SetLED(self._window, '-HEARTBEAT-', "gray")

statusbar = StatusBar(key="-STATUS_BAR-")


def handler(event, values, window):
    if event == sg.WINDOW_CLOSED or event == "-EXIT-":
      window.close()