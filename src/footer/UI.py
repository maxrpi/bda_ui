import PySimpleGUI as sg

layout = [[
  sg.Exit(key="-EXIT-"),
  sg.B("Save state", enable_events=True, key="-SAVE_STATE-"),
  sg.B("Load state", enable_events=True, key="-LOAD_STATE-")
]]

def handler(event, values, window):
    if event == sg.WINDOW_CLOSED or event == "-EXIT-":
      window.close()