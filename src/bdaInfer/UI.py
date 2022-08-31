from pathlib import Path
import PySimpleGUI as sg
import bda_service
import refresher
from footer import statusbar

known_mkos = {}
ready_mkos = []
pending_mkos = []
filecounter = 0
smip_auth = {}
my_settings_copy = {}
mko_table = [[]]
progress_bars = {}

layout = [
  [
    sg.T("CREATE ANALYSIS")
  ],
  [ 
    sg.T("PENDING MKOs")
  ],
  [
    sg.Listbox([],
      size=(12,10),
      select_mode="LISTBOX_SELECT_MODE_SINGLE",
      key="-READY_MKOS-"
      ),
    sg.Column([
      [
      sg.In("", visible=False, enable_events=True, key="-LOAD_MKO_FILENAME-"),
      sg.FileBrowse("Load MKO",
        file_types=[('MKO','*.mko')],
        key='-DOWNLOAD_MKO-',
        enable_events=True)
      ],
      [
      sg.In("", visible=False, enable_events=True, key="-SAVE_MKO_FILENAME-"),
      sg.SaveAs("Save MKO",
        default_extension=".mko", file_types=[('MKO','*.mko')],
        key='-SAVE_MKO-',
        enable_events=True)
      ],
    ]),
    sg.ButtonMenu("Analysis Types",
      menu_def=['Unused', ['time predictor', 'integrator', 'sampler', 'plot']],
      key="-ANALYSIS_TYPE-"),
    sg.Frame("Options", layout=[[]], size=(200,200)),
  ],
  [
    sg.Table(values=mko_table,
      headings=["MKO", "Stage" ,"Progress"],
      col_widths = [12, 5, 11],
      auto_size_columns=False,
      justification='center',
      background_color="white",
      text_color="black",
      key="-PENDING_MKOS-",
      display_row_numbers=False,
      num_rows=5,
      expand_x=False,
      vertical_scroll_only=True
      ),
  ]
]

class Element(object):
  def __init__(self):
    pass

  def set_refresh_function(self, refresh_function):
    self._refresh_function = refresh_function
  
  def refresh(self):
    self._refresh_function()

  @property
  def unqueue(self):
    return False
    
pending_table = Element()

def add_mko(mko, window):
  global known_mkos
  global ready_mkos
  global pending_mkos
  
  known_mkos[mko.name] = mko
  if mko.name in pending_mkos:
    pending_mkos.remove(mko.name)
  elif mko.name in ready_mkos:
    ready_mkos.remove(mko.name)
  else:
    pass
  if not mko.ready: 
    pending_mkos.append(mko.name)
  else:
    ready_mkos.append(mko.name)
  
  window['-READY_MKOS-'].update(values=ready_mkos)

  update_pending_table(window)

  def make_refresh():
    update_pending_table(window)
  
  pending_table.set_refresh_function(make_refresh)
  refresher.refresh_daemon.add_task(pending_table)
  

def update_pending_table(window):
  global pending_mkos, known_mkos, progress_bars
  for mko_name in list(pending_mkos):
    mko = known_mkos[mko_name]
    if mko.ready and mko not in ready_mkos:
      pending_mkos.remove(mko_name)
      ready_mkos.append(mko_name)
      mko.set_unqueue()
      continue
    if mko.unqueue:
      pending_mkos.remove(mko_name)
      continue
    x = int(10 * mko.progress)
    progress_string = "*" * x + "-" * (10-x)
    progress_bars[mko_name] = progress_string

  pending_table = [ [name, known_mkos[name].stage, progress_bars[name] ] for name in pending_mkos]

  window['-PENDING_MKOS-'].update(values=pending_table )
  window['-READY_MKOS-'].update(values=ready_mkos )
  
  
  
def handler(event, values, window):
  global pending_mkos, ready_mkos, known_mkos
  global filecounter

  if event == "-SAVE_MKO_FILENAME-":
    filename = values['-SAVE_MKO_FILENAME-']
    ready_index = window['-READY_MKOS-'].get_indexes()[0]
    mko = known_mkos[ready_mkos[ready_index]]
    mko.save_to_file(filename)
    return True


  if event == "-LOAD_MKO_FILENAME-":
    if bda_service.bda_service == None:
      statusbar.update("Cannot load MKO into service: not logged in.")
      return True
    filename = values['-LOAD_MKO_FILENAME-']
    name = Path(filename).stem
    if name in known_mkos:
      filecounter += 1
      name = name + "({})".format(filecounter)
    mko = bda_service.MKO(name, bda_service.bda_service.current_user, bda_service)
    
    known_mkos[name] = mko
    mko.load_from_file(filename)
    ready_mkos.append(name)
    window['-READY_MKOS-'].update(values=ready_mkos )
    return True

  return False