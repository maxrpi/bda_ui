#!/usr/bin/env python
from pathlib import Path
import PySimpleGUI as sg
import smip
import bdaTrain
import footer
from support_functions.uifunctions import settings


tab_group = sg.TabGroup([[
  sg.Tab('SMIP', smip.layout),
  sg.Tab('BDA Training', bdaTrain.layout),
  ]])

layout = [[tab_group],[footer.layout]]

if __name__ == "__main__":
  
  window = sg.Window('BDA Service Interface App', layout, finalize=True)
  smip.assign_settings(settings['SMIP'], window)
  bdaTrain.assign_settings(settings['BDA'], window)

  while True:
    event, values = window.read()
    try:
      if smip.handler(event, values, window,
          token_to_BDA=bdaTrain.set_smip_auth,
          attrib_to_BDA=bdaTrain.add_attribute):
        continue
      if bdaTrain.handler(event, values, window):
        continue
      if footer.handler(event, values, window):
        continue
    except Exception as err:
      print(err)


    if event == sg.WINDOW_CLOSED or event == "-EXIT-":
      break

  window.close()
