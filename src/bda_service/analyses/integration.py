import PySimpleGUI as sg
import numpy as np
import pandas as pd

from support_functions import encodings
from bda_service.analyses import Analysis

class Integration(Analysis):
  def __init__(self, name, mko, service, analysis_data) -> None:
    super().__init__(name,"integration", mko, service, analysis_data)
    self._endpoint = "/Analyze/integrate"
    self._direct_response = False

  def query_data(self) -> dict:
    mko_data = self._mko.contents
    input_df = pd.read_csv(self._analysis_data['input_filename'])
    mapping =  dict(zip(input_df.columns, [ col.lstrip().rstrip() for col in input_df.columns]))
    input_df = input_df.rename(columns=mapping)
    cols = self._mko.dataspec['inputs']
    inputs = encodings.b64encode_datatype(input_df[cols].to_numpy())
    table_df = pd.read_csv(self._analysis_data['function_filename'])
    mapping =  dict(zip(table_df.columns, [ col.lstrip().rstrip() for col in table_df.columns]))
    table_df = table_df.rename(columns=mapping)
    cols = self._mko.dataspec['outputs'] + ['function']
    table = encodings.b64encode_datatype(table_df[cols].to_numpy())
    n_samples = self._analysis_data.get('n_samples', "0")
    try: int(n_samples)
    except: n_samples = 0
    
    return {
      "mko" : mko_data,
      "inputs": inputs,
      "n_samples" : n_samples,
      "function" : table,
    }
  
  def format_contents_as_string(self):
    if not self.ready:
      raise Exception("Not ready")

    string = self.contents

    return string

  def display_in_window(self):
    window = sg.Window("MKO",
      [
        [ sg.Text("Integral:", enable_events=False), ],
        [ sg.Output(size=(250,300), key="-OUTPUT_BOX-") ],
        [ sg.B("EXIT", enable_events=True, key="-EXIT-") ],
      ]
    , finalize=True, size=(400,400))
    
    string = self.format_contents_as_string()
    window['-OUTPUT_BOX-'].update(string)

    while True:
      event, values = window.read()
      if event == sg.WINDOW_CLOSED or event == "-EXIT-":
        break
    window.close()
