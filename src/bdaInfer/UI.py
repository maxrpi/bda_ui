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
  mko_keys : list[str]
  known_analyses = {}
  ready_analyses = []
  pending_analyses = []
  pending_analyses_table = refresher.Element()
  analyses_progress_bars = {}
  current_analysis = list(analysisUIs.keys())[0]
  options_UI = analysisUIs[current_analysis]
  analysis_obj = analysis_types[current_analysis]


def add_mko(mko : bda_service.MKO, name, window):
  bi.known_mkos[name] = mko
  bi.mko_keys = list(bi.known_mkos.keys())
  bi.mko_keys.sort()
  window['-BI_AVAILABLE_MKOS-'].update(bi.mko_keys)

def delete_mko(name, window):
  if name in bi.known_mkos:
    del bi.known_mkos[name]
  bi.mko_keys = list(bi.known_mkos.keys())
  bi.mko_keys.sort()
  window['-BI_AVAILABLE_MKOS-'].update(bi.mko_keys)


def add_analysis(analysis, window):
  
  if analysis.name in bi.known_analyses:
    bi.known_analyses[analysis.name].set_unqueue()
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
  new_analyses = []
  for analysis_name in list(bi.pending_analyses):
    analysis = bi.known_analyses[analysis_name]
    if analysis.ready and analysis not in bi.ready_analyses:
      bi.pending_analyses.remove(analysis_name)
      bi.ready_analyses.append(analysis_name)
      new_analyses.append(analysis_name)
      analysis.set_unqueue()
      continue
    if analysis.unqueue:
      bi.pending_analyses.remove(analysis_name)
      continue
    x = int(10 * analysis.progress)
    progress_string = "*" * x + "-" * (10-x)
    bi.analyses_progress_bars[analysis_name] = progress_string

  pending_table = [
    [name, bi.analyses_progress_bars[name] ]
    for name in bi.pending_analyses ]

  window['-PENDING_ANALYSES-'].update(values=pending_table )
  window['-READY_ANALYSES-'].update(values=bi.ready_analyses )
  if len(new_analyses) > 1:
    statusbar.update("Analyses ready: {}".format(",".join(new_analyses)))
  elif len(new_analyses) == 1:
    statusbar.update("Analysis {} ready".format(new_analyses[0]))
  else:
    pass



  
def handler(event, values, window):

  if event == "-ANALYSIS_TABGR-":
    bi.current_analysis = window[event].get()
    bi.options_UI = analysisUIs[bi.current_analysis]
    bi.analysis_obj = analysis_types[bi.current_analysis]
    return True
  
  if event == bi.options_UI.go_tag:
    selected_indices = window['-BI_AVAILABLE_MKOS-'].get_indexes()
    if len(selected_indices) == 0:
      statusbar.error("No MKO selected for analysis {}".format(bi.current_analysis))
      return True
    ready_index = selected_indices[0]
    mko_name = bi.mko_keys[ready_index]
    mko = bi.known_mkos[mko_name]
    analysis = bi.analysis_obj(bi.options_UI.name, mko, bda_service.service, bi.options_UI.analysis_data)
    bda_service.service.launch_analysis(analysis)
    add_analysis(analysis, window)
    refresher.refresh_daemon.add_task(analysis)
    statusbar.update(f"Queuing {mko_name} for {bi.current_analysis}")
    return True
    
  if event == "-BI_DELETE_AVAILABLE_MKO-":
    selected_indices = window['-BI_AVAILABLE_MKOS-'].get_indexes()
    if len(selected_indices) == 0:
      statusbar.error("No MKO selected to delete")
      return True
    ready_index = selected_indices[0]
    mko_name = bi.mko_keys[ready_index]
    delete_mko(mko_name, window)

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
  
  if event == "-BI_DELETE_ANALYSIS-":
    selected_indices = window['-READY_ANALYSES-'].get_indexes()
    if len(selected_indices) == 0:
      statusbar.update("NO ANALYSIS SELECTED TO DELETE")
      return True
    ready_index = selected_indices[0]
    name = bi.ready_analyses[ready_index]
    bi.ready_analyses.remove(name)
    window['-READY_ANALYSES-'].update(values=bi.ready_analyses)
    del bi.known_analyses[name]


  if event == "-UNQUEUE_ANALYSES-":
    statusbar.update("Unqueuing all pending analyses")
    for analysis_name in list(bi.pending_analyses):
      analysis = bi.known_analyses[analysis_name]
      analysis.set_unqueue()
      del bi.known_analyses[analysis_name]
      bi.pending_analyses.remove(analysis_name)
    update_pending_analyses_table(window)
    return True

  if bi.options_UI.handler(event, values, window):
    return True

  return False