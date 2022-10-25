import PySimpleGUI as sg
import pandas as pd
import re
from pathlib import Path
import bda_service
import refresher
from bdaTrain.layout import layout, number_of_layers, layer_keys
import bdaTrain.curator as curator
from footer import statusbar

class bt():
  settings = {}

  known_mkos : dict[str, bda_service.MKO] = {}
  prepped_mkos : dict[str, bda_service.MKO] = {}
  prepped_mko_keys : list[str] = []
  inprogress_mkos = []
  ready_mkos = []
  inprogress_mko_table = refresher.Element()
  mko_progress_bars = {}
  ondeck : bda_service.MKO
  filecounter = 0
  

def initialize(settings, window):
  assign_settings(window, settings)
  set_bindings(window)

def assign_settings(window, settings):
  bt.settings = settings
  if bt.settings['start_time'] is not None: window['-TS_START_TIME-'].update(bt.settings['start_time']) 
  if bt.settings['end_time'] is not None: window['-TS_END_TIME-'].update(bt.settings['end_time']) 
  if bt.settings['sample_period'] is not None: window['-TS_SAMPLE_PERIOD-'].update(bt.settings['sample_period']) 
  if bt.settings['number_samples'] is not None: window['-TS_NUMBER_SAMPLES-'].update(bt.settings['number_samples']) 

def set_bindings(window):
  window['-TS_PARSE_START-'].bind('<KeyPress-Return>','RETURN')
  window['-TS_PARSE_END-'].bind('<KeyPress-Return>','RETURN')
  window['-TS_SAMPLE_PERIOD-'].bind('<KeyPress-Return>','RETURN')
  window['-TS_NUMBER_SAMPLES-'].bind('<KeyPress-Return>','RETURN')

def unique_name(name: str):
  bt.filecounter += 1
  pattern = re.compile(r"(.+)\.(\d+)")
  m = pattern.fullmatch(name)
  if m != None:
    stem = m.group(1)
  else:
    stem = name

  return f"{stem}.{bt.filecounter}"

def delete_mko_from_prepped(mko, window):
  if mko.name not in bt.prepped_mkos:
    return
  del bt.prepped_mkos[mko.name]
  bt.prepped_mko_keys = list(bt.prepped_mkos)
  bt.prepped_mko_keys.sort()
  tmp = [[bt.prepped_mkos[n].name, bt.prepped_mkos[n].stage]
          for n in bt.prepped_mko_keys]
  window['-BT_PREPPED_MKOS-'].update(values=tmp)

def add_mko_to_prepped(mko: bda_service.MKO, window):
  mko.set_progress(0.0)
  mko.set_autoprogress(False)
  bt.prepped_mkos[mko.name] = mko
  bt.prepped_mko_keys = list(bt.prepped_mkos)
  bt.prepped_mko_keys.sort()
  tmp = [[bt.prepped_mkos[n].name, bt.prepped_mkos[n].stage]
          for n in bt.prepped_mko_keys]
  window['-BT_PREPPED_MKOS-'].update(values=tmp)

def add_mko_to_inprogress(mko : bda_service.MKO, window):
  mko.set_autoprogress(True)
  mko.set_inprocess(False)
  refresher.refresh_daemon.add_task(mko)
  bt.inprogress_mkos.append(mko.name)
  update_inprogress_mko_table(window)
  def make_refresh():
    update_inprogress_mko_table(window)
  bt.inprogress_mko_table.set_refresh_function(make_refresh)
  refresher.refresh_daemon.add_task(bt.inprogress_mko_table)
  

def update_inprogress_mko_table(window):
  for mko_name in list(bt.inprogress_mkos):
    mko = bt.known_mkos[mko_name]
    if mko.ready:
      bt.inprogress_mkos.remove(mko_name)
      if mko.name not in bt.ready_mkos:
        bt.ready_mkos.append(mko_name)
      else:
        statusbar.update("Updating MKO {} in READY MKOs list".format(mko.name))
      mko.set_unqueue()
      window['-DT_READY_MKOS-'].update(values=bt.ready_mkos )
      continue
    if mko.unqueue:
      bt.inprogress_mkos.remove(mko_name)
      continue
    x = int(10 * mko.progress)
    progress_string = "*" * x + "-" * (10-x)
    bt.mko_progress_bars[mko_name] = progress_string
  inprogress_table = [
    [name, bt.known_mkos[name].stage, bt.mko_progress_bars[name] ]
    for name in bt.inprogress_mkos ]
  window['-IN_PROGRESS_MKOS-'].update(values=inprogress_table )
      
def load_mko_from_file(filename):
  if bda_service.service == None:
    statusbar.update("Cannot load MKO into service: not logged in.")
    raise ConnectionError("Service not connected")
  name = Path(filename).stem
  if name in bt.known_mkos:
    bt.filecounter += 1
    name = name + "({})".format(bt.filecounter)
  mko = bda_service.MKO(name, bda_service.service.current_user, bda_service.service)
  bt.known_mkos[name] = mko
  mko.load_from_file(filename)
  dataspec = bda_service.service.get_mko_as_dict(mko)['dataspec']
  mko.incorporate_dataspec(dataspec)
  return mko, name

def send_to_ondeck(mko, values, window):
  bt.ondeck = mko
  window['-DT_ONDECK_MKO-'].update(mko.name)
  try:
    hypers = curator.get_hypers_from_mko(bda_service.service, mko)
    curator.hypers_to_ui(hypers, window)
    topology = curator.get_topology_from_mko(bda_service.service, mko)
    curator.topology_to_ui(topology, window)
  except: # Nothing essential here.
    pass
  window['-DT_TRAIN_AS_NAME-'].update(unique_name(mko.name))
  show_layer_options(values, window)
  return

def train_ondeck(values,window):
  if not isinstance(bt.ondeck, bda_service.MKO):
    statusbar.error("NO MKO ONDECK TO TRAIN")
    return True
  new_name = values['-DT_TRAIN_AS_NAME-']
  if new_name == "":
    statusbar.error("Training name needed")
    return True
  new_mko = bt.ondeck.copy(new_name)
  topology = curator.get_layer_spec(values)
  new_mko.set_topology(topology)
  hypers = curator.get_hyperparameter_spec(values)
  new_mko.set_hypers(hypers)
  new_mko.set_autocalibrate(values['-DT_AUTOCALIBRATE-'])
  new_mko.set_smip_auth(bda_service.service.smip_auth)
  bt.known_mkos[new_name] = new_mko
  new_mko.set_inprocess(True)
  if new_mko.stage == 3:
    new_mko.set_stage(1)
  add_mko_to_inprogress(new_mko, window)
  window["-DT_TRAIN_AS_NAME-"].update(unique_name(new_name))
  return True

def show_layer_options(values, window):
  show_autocalibrate = False
  for i in range(number_of_layers):
    l_type = values[layer_keys['type'].format(i)]
    if l_type == 'variational': l_type = 'variational_dropout'
    if l_type == "-":
      window[layer_keys['activation'].format(i)].update(visible=False)
      window[layer_keys['units'].format(i)].update(visible=False)
    else:
      window[layer_keys['activation'].format(i)].update(visible=True)
      window[layer_keys['units'].format(i)].update(visible=True)
      window[layer_keys['lambda'].format(i)].update(visible=True)
      window[layer_keys['regularizer'].format(i)].update(visible=True)
    if l_type in ["dropout", "variational_dropout"]:
      window[layer_keys['rate'].format(i)].update(visible=True)
    else:
      window[layer_keys['rate'].format(i)].update(visible=False)
    if l_type in ["variational_dropout"]:
      show_autocalibrate=True
    
    if l_type in ['variational_dropout', 'dropout', 'dense']:
      window[layer_keys['regularizer'].format(i)].update(visible=True)
      window[layer_keys['lambda'].format(i)].update(visible=True)
    else:
      window[layer_keys['regularizer'].format(i)].update(visible=False)
      window[layer_keys['lambda'].format(i)].update(visible=False)

  if show_autocalibrate:
    window["-DT_AUTOCALIBRATE-"].update(disabled=False)
  else:
    window["-DT_AUTOCALIBRATE-"].update(value=False, disabled=True)
    
def handler(event, values, window, add_mko_to_infer):

  show_layer_options(values, window)

  if event == "-BT_PREPPED_MKOS-":
    selected_indices = values['-BT_PREPPED_MKOS-']
    prepped_index = selected_indices[0]
    mko = bt.prepped_mkos[bt.prepped_mko_keys[prepped_index]]
    window["-DT_SOURCE_MKO-"].update(mko.name)
    window["-DT_TRAIN_AS_NAME-"].update(mko.name)
    return True

  if event == "-TRAIN_MKO-":
    try:
      train_ondeck(values, window)
    except:
      pass
    return True

  if event == "-DT_PREPPED_TO_ONDECK-":
    selected_indices = values['-BT_PREPPED_MKOS-']
    if len(selected_indices) == 0:
      statusbar.update("NO MKO SELECTED TO DELETE")
      return True
    prepped_index = selected_indices[0]
    mko = bt.prepped_mkos[bt.prepped_mko_keys[prepped_index]]
    send_to_ondeck(mko, values, window)
    return True

  if event == "-DT_PREPPED_DELETE-":
    selected_indices = values['-BT_PREPPED_MKOS-']
    if len(selected_indices) == 0:
      statusbar.update("NO MKO SELECTED TO DELETE")
      return True
    prepped_index = selected_indices[0]
    mko = bt.prepped_mkos[bt.prepped_mko_keys[prepped_index]]
    delete_mko_from_prepped(mko, window)
    statusbar.update(f"DELETED MKO {mko.name}")
    return True

  if event == "-DT_READY_TO_ONDECK-":
    selected_indices = window['-DT_READY_MKOS-'].get_indexes()
    if len(selected_indices) == 0:
      statusbar.update("NO MKO SELECTED TO SEND TO ON-DECK")
      return True
    ready_index = selected_indices[0]
    mko = bt.known_mkos[bt.ready_mkos[ready_index]]
    send_to_ondeck(mko, values, window)
    return True

  if event == "-DT_DELETE_READY-":
    selected_indices = window['-DT_READY_MKOS-'].get_indexes()
    if len(selected_indices) == 0:
      statusbar.update("NO MKO SELECTED TO DELETE")
      return True
    ready_index = selected_indices[0]
    name = bt.ready_mkos[ready_index]
    bt.ready_mkos.remove(name)
    del bt.known_mkos[name]
    window['-DT_READY_MKOS-'].update(values=bt.ready_mkos )
    return True

  if event == "-DT_TO_INFER-":
    selected_indices = window['-DT_READY_MKOS-'].get_indexes()
    if len(selected_indices) == 0:
      statusbar.update("NO MKO SELECTED TO SEND TO INFER")
      return True
    ready_index = selected_indices[0]
    mko = bt.known_mkos[bt.ready_mkos[ready_index]]
    add_mko_to_infer(mko, bt.ready_mkos[ready_index], window)

  if event == "-DT_READY_SAVE-":
    selected_indices = window['-DT_READY_MKOS-'].get_indexes()
    if len(selected_indices) == 0:
      statusbar.update("NO MKO SELECTED TO SAVE")
      return True
    filename = values['-DT_READY_SAVE-']
    ready_index = selected_indices[0]
    mko = bt.known_mkos[bt.ready_mkos[ready_index]]
    mko.save_to_file(filename)
    return True

  if event == "-DT_READY_LOAD-":
    try:
      filename = values['-DT_READY_LOAD-']
      mko, name = load_mko_from_file(filename)
      mko.set_stage(3)
      bt.ready_mkos.append(name)
      window['-DT_READY_MKOS-'].update(values=bt.ready_mkos )
      statusbar.update(f"Loaded MKO {mko.name} from file {filename}")
    except bda_service.BDAServiceException as err:
      statusbar.error("Cannot load MKO. Are you logged in?")
    return True

  if event == "-UNQUEUE_MKOS-":
    statusbar.update("Unqueuing all inprogress MKOs")
    for mko_name in list(bt.inprogress_mkos):
      mko = bt.known_mkos[mko_name]
      mko.set_unqueue()
      bt.inprogress_mkos.remove(mko_name)
      mko.set_stage(0)
    update_inprogress_mko_table(window)
    return True

  return False