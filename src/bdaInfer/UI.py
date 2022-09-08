from pathlib import Path
import PySimpleGUI as sg
import bda_service
from bda_service.analyses import analysis_types, Analysis
from bdaInfer.layout import layout
import refresher
from footer import statusbar
from bdaInfer.analysisUIs import AnalysisUI
from bdaInfer.analysisUIs import UIs as analysisUIs

class bi():
  settings = {}
  smip_auth = {}

  known_mkos = {}
  ready_mkos = []
  pending_mkos = []
  pending_mko_table = refresher.Element()
  mko_progress_bars = {}

  filecounter = 0
  known_analyses = {}
  ready_analyses = []
  pending_analyses = []
  pending_analyses_table = refresher.Element()
  analyses_progress_bars = {}
  current_analysis = list(analysisUIs.keys())[0]
  options_UI = analysisUIs[current_analysis]
  analysis_obj = analysis_types[current_analysis]


def add_mko(mko, window):
  
  bi.known_mkos[mko.name] = mko
  if mko.name in bi.pending_mkos:
    bi.pending_mkos.remove(mko.name)
  elif mko.name in bi.ready_mkos:
    bi.ready_mkos.remove(mko.name)
    
  if not mko.ready: 
    bi.pending_mkos.append(mko.name)
  else:
    bi.ready_mkos.append(mko.name)
  
  window['-READY_MKOS-'].update(values=bi.ready_mkos)

  update_pending_mko_table(window)
  def make_refresh():
    update_pending_mko_table(window)
  bi.pending_mko_table.set_refresh_function(make_refresh)
  refresher.refresh_daemon.add_task(bi.pending_mko_table)
  

def update_pending_mko_table(window):
  for mko_name in list(bi.pending_mkos):
    mko = bi.known_mkos[mko_name]
    if mko.ready and mko not in bi.ready_mkos:
      bi.pending_mkos.remove(mko_name)
      bi.ready_mkos.append(mko_name)
      mko.set_unqueue()
      continue
    if mko.unqueue:
      bi.pending_mkos.remove(mko_name)
      continue
    x = int(10 * mko.progress)
    progress_string = "*" * x + "-" * (10-x)
    bi.mko_progress_bars[mko_name] = progress_string

  pending_table = [
    [name, bi.known_mkos[name].stage, bi.mko_progress_bars[name] ]
    for name in bi.pending_mkos ]

  window['-PENDING_MKOS-'].update(values=pending_table )
  window['-READY_MKOS-'].update(values=bi.ready_mkos )

def add_analysis(analysis, window):
  
  bi.known_analyses[analysis.name] = analysis
  if analysis.name in bi.pending_analyses:
    bi.pending_analyses.remove(analysis.name)
  elif analysis.name in bi.ready_analyses:
    bi.ready_analyses.remove(analysis.name)
    
  if not analysis.ready: 
    bi.pending_analyses.append(analysis.name)
  else:
    bi.ready_analyses.append(analysis.name)
  
  window['-READY_ANALYSES-'].update(values=bi.ready_analyses)

  update_pending_analyses_table(window)
  def make_refresh():
    update_pending_analyses_table(window)
  bi.pending_analyses_table.set_refresh_function(make_refresh)
  refresher.refresh_daemon.add_task(bi.pending_analyses_table)
  

def update_pending_analyses_table(window):
  for analysis_name in list(bi.pending_analyses):
    analysis = bi.known_analyses[analysis_name]
    if analysis.ready and analysis not in bi.ready_analyses:
      bi.pending_analyses.remove(analysis_name)
      bi.ready_analyses.append(analysis_name)
      analysis.set_unqueue()
      continue
    if analysis.unqueue:
      bi.pending_analyses.remove(analysis_name)
      continue
    x = int(10 * analysis.progress)
    progress_string = "*" * x + "-" * (10-x)
    bi.mko_progress_bars[analysis_name] = progress_string

  pending_table = [
    [name, bi.known_analyses[name].stage, bi.analyses_progress_bars[name] ]
    for name in bi.pending_analyses ]

  window['-PENDING_ANALYSES-'].update(values=pending_table )
  window['-READY_ANALYSES-'].update(values=bi.ready_analyses )
  


  
def handler(event, values, window):

  if event == "-SAVE_MKO_FILENAME-":
    selected_indices = window['-READY_MKOS-'].get_indexes()
    if len(selected_indices) == 0:
      statusbar.update("NO MKO SELECTED TO SAVE")
      return True
    filename = values['-SAVE_MKO_FILENAME-']
    ready_index = selected_indices[0]
    mko = bi.known_mkos[bi.ready_mkos[ready_index]]
    mko.save_to_file(filename)
    return True


  if event == "-LOAD_MKO_FILENAME-":
    if bda_service.service == None:
      statusbar.update("Cannot load MKO into service: not logged in.")
      return True
    filename = values['-LOAD_MKO_FILENAME-']
    name = Path(filename).stem
    if name in bi.known_mkos:
      bi.filecounter += 1
      name = name + "({})".format(bi.filecounter)
    mko = bda_service.MKO(name, bda_service.service.current_user, bda_service)
    bi.known_mkos[name] = mko
    mko.load_from_file(filename)
    bi.ready_mkos.append(name)
    window['-READY_MKOS-'].update(values=bi.ready_mkos )
    return True
  if event == "-UNQUEUE_MKOS-":
    statusbar.update("Unqueuing all pending MKOs")
    for mko_name in list(bi.pending_mkos):
      mko = bi.known_mkos[mko_name]
      mko.set_unqueue()
      del bi.known_mkos[mko_name]
      bi.pending_mkos.remove(mko_name)
    update_pending_mko_table(window)
    return True

  if event == "-ANALYSIS_TABGR-":
    bi.current_analysis = window[event].get()
    bi.options_UI = analysisUIs[bi.current_analysis]
    bi.analysis_obj = analysis_types[bi.current_analysis]
    return True
  
  if event == bi.options_UI.go_tag:
    selected_indices = window['-READY_MKOS-'].get_indexes()
    if len(selected_indices) == 0:
      statusbar.update("NO MKO SELECTED FOR ANALYSIS {}".format(bi.current_analysis))
      return True
    ready_index = selected_indices[0]
    mko = bi.known_mkos[bi.ready_mkos[ready_index]]
    analysis = bi.analysis_obj(bi.current_analysis, mko, bda_service.service, bi.options_UI.analysis_data)
    bda_service.service.launch_analysis(analysis)
    add_analysis(analysis, window)
    return True

  if event == "-DISPLAY_ANALYSIS-":
    refresher.refresh_daemon.pause()
    selected_indices = window['-READY_ANALYSES-'].get_indexes()
    if len(selected_indices) == 0:
      statusbar.update("NO ANALYSIS SELECTED TO DISPLAY")
      return True
    ready_index = selected_indices[0]
    analysis = bi.known_analyses[bi.ready_analyses[ready_index]]
    analysis.display_in_window()
    refresher.refresh_daemon.unpause()
    return True

  if bi.options_UI.handler(event, values, window):
    return True

  return False