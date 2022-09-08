#!/usr/bin/env python
from pathlib import Path
import PySimpleGUI as sg
from bdaInfer.UI import add_mko
import refresher
import smip
import bdaTrain
import bdaInfer
import footer
from support_functions.uifunctions import settings

import refresher
refresher.refresh_daemon.initialize(10)
refresher.refresh_daemon.run()

tab_group = sg.TabGroup([[
  sg.Tab('SMIP', smip.layout),
  sg.Tab('BDA Training', bdaTrain.layout),
  sg.Tab('BDA Infer', bdaInfer.layout),
  ]])

layout = [[tab_group],[footer.layout]]

if __name__ == "__main__":
  
  window = sg.Window('BDA Service Interface App', layout, finalize=True)
  smip.assign_settings(settings['SMIP'], window)
  smip.set_bindings(window)
  bdaTrain.assign_settings(settings['BDAtrain'], window)
  bdaTrain.set_bindings(window)
  footer.statusbar.register_statusbar(window)

  while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED or event == "-EXIT-":
      break

    try:
      if smip.handler(event, values, window,
          token_to_BDA=bdaTrain.set_smip_auth,
          attrib_to_BDA=bdaTrain.add_attribute
          ):
        continue
      if bdaTrain.handler(event, values, window,
        get_timeseries_array=smip.get_timeseries_array,
        add_mko_to_infer=bdaInfer.add_mko
        ):
        continue
      if bdaInfer.handler(event, values, window,):
        continue
      if footer.handler(event, values, window):
        continue
    except Exception as err:
      print(err)



  window.close()

