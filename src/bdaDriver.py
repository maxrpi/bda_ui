#!/usr/bin/env python
from pathlib import Path
import PySimpleGUI as sg
from bdaInfer.UI import add_mko as add_mko_to_infer
from bda_service import service
import refresher
import smip
import bdaLogins
import bdaData
import bdaTrain
import bdaInfer

import footer
from support_functions.uifunctions import settings

import refresher
refresher.refresh_daemon.initialize(10)
refresher.refresh_daemon.run()

tab_group = sg.TabGroup([[
  sg.Tab('BDA Logins', bdaLogins.layout),
  sg.Tab('SMIP', smip.layout),
  sg.Tab('BDA Data', bdaData.layout),
  sg.Tab('BDA Training', bdaTrain.layout),
  sg.Tab('BDA Infer', bdaInfer.layout),
  ]])

layout = [[tab_group],[footer.layout]]

if __name__ == "__main__":
  
  window = sg.Window('BDA Service Interface App', layout, finalize=True)
  smip.assign_settings(settings['SMIP'], window)
  smip.set_bindings(window)
  bdaLogins.initialize(settings['BDAlogins'], window)
  bdaData.initialize(settings['BDAdata'], window)
  bdaTrain.initialize(settings['BDAtrain'], window)
  footer.statusbar.register_statusbar(window)

  while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED or event == "-EXIT-":
      break

    try:
      if smip.handler(event, values, window,
          token_to_BDA=service.set_smip_auth,
          ts_to_BDA=bdaData.add_timeseries,
          ls_to_BDA=bdaData.add_lot_series,
          ):
        continue
      if bdaLogins.handler(event, values, window):
        continue
      if bdaData.handler(event, values, window,
        get_timeseries_array=smip.get_timeseries_array,
        get_lot_series=smip.get_lot_series,
        add_mko_to_train=bdaTrain.add_mko_to_train,
        ):
        continue
      if bdaTrain.handler(event, values, window,
        add_mko_to_infer=add_mko_to_infer,
        ):
        continue
      if bdaInfer.handler(event, values, window,):
        continue
      if footer.handler(event, values, window):
        continue
    except Exception as err:
      print(err)



  window.close()

