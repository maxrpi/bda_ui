import PySimpleGUI as sg
import bda_service
import refresher

known_attributes = {}
avail_keys = list(known_attributes.keys())
inputs_keys = []
outputs_keys = []
top_text_width=16
sorter_width = 30
bda_token_expiration = "no token"
smip_auth = {}
startTimeObj = None
endTimeObj = None
my_settings_copy = {}
user = None
mko_table = [[]]

layout = [
  [
    sg.T("CREATE ANALYSIS")
  ],
  [ 
    sg.T("AVAILABLE MKOs")
  ],
  [
    sg.Table(values=mko_table,
           headings=["MKO", "status"],
           max_col_width=15,
           auto_size_columns=False,
           justification='center',
           background_color="white",
           text_color="black",
           enable_events=True,
           key="-MKO_LIST-",
           display_row_numbers=False,
           num_rows=10,
           expand_x=False,
           vertical_scroll_only=True
           ),
    sg.ButtonMenu("Analysis Types",
          menu_def=['Unused', ['time predictor', 'integrator', 'sampler', 'plot']],
          key="-ANALYSIS_TYPE-"),
    sg.Frame("Options", layout=[[]], size=(200,200)),
  ]
]