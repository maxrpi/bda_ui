from turtle import pen
import PySimpleGUI as sg
import bda_service
import refresher

known_mkos = {}
ready_mkos = []
pending_mkos = []
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
      size=(14,8),
      select_mode="LISTBOX_SELECT_MODE_SINGLE",
      key="-READY_MKOS-"
      ),
    sg.ButtonMenu("Analysis Types",
      menu_def=['Unused', ['time predictor', 'integrator', 'sampler', 'plot']],
      key="-ANALYSIS_TYPE-"),
    sg.Frame("Options", layout=[[]], size=(200,200)),
  ],
  [
    sg.Table(values=mko_table,
      headings=["MKO", "Stage" ,"Progress"],
      col_widths = [10, 6, 14],
      auto_size_columns=False,
      justification='center',
      background_color="white",
      text_color="black",
      key="-PENDING_MKOS-",
      display_row_numbers=False,
      num_rows=9,
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
  def complete(self):
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
  for pending_mko in pending_mkos:
    x = int(10 * known_mkos[pending_mko].progress)
    progress_string = "*" * x + "-" * (10-x)
    progress_bars[pending_mko] = progress_string

  pending_table = [ [name, known_mkos[name].stage, progress_bars[name] ] for name in pending_mkos]

  window['-PENDING_MKOS-'].update(values=pending_table )
  
  
  
def handler(event, values, window):
  global pending_mkos, ready_mkos, known_mkos
  return False