#!/usr/bin/env python
from pathlib import Path
import PySimpleGUI as sg
import refresher
import smip
import bdaTrain
import footer
from support_functions.uifunctions import settings

import refresher
refresher.refresh_daemon = refresher.RefreshDaemon(60)
refresher.refresh_daemon.run()

tab_group = sg.TabGroup([[
  sg.Tab('SMIP', smip.layout),
  sg.Tab('BDA Training', bdaTrain.page.layout),
  ]])

layout = [[tab_group],[footer.layout]]

if __name__ == "__main__":
  
  window = sg.Window('BDA Service Interface App', layout, finalize=True)
  smip.assign_settings(settings['SMIP'], window)
  smip.set_bindings(window)
  bdaTrain.page.set_settings(settings)
  bdaTrain.page.initialize(window)

  while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED or event == "-EXIT-":
      break

    try:
      if smip.handler(event, values, window,
          token_to_BDA=bdaTrain.set_smip_auth,
          attrib_to_BDA=bdaTrain.add_attribute):
        continue
      if bdaTrain.page.event_handler(event, values, window,
        get_timeseries_array=smip.get_timeseries_array):
        continue
      if footer.handler(event, values, window):
        continue
    except Exception as err:
      print(err)



  window.close()

