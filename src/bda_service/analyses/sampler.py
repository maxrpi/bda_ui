import PySimpleGUI as sg
import numpy as np
import json
from io import StringIO
import pandas as pd
import support_functions.encodings as encodings

from bda_service.analyses import Analysis

class Sampler(Analysis):
  def __init__(self, name, mko, service, analysis_data) -> None:
    super().__init__(name,"sampler", mko, service, analysis_data)
    self._endpoint = "/Infer/sample"
    self._direct_response = True

  def query_data(self) -> dict:
    ''' Note that inputs ends up as list, not numpy.ndarray type '''
    mko_data = self._mko.contents
    input_df = pd.read_csv(self._analysis_data['input_filename'])
    mapping =  dict(zip(input_df.columns, [ col.lstrip().rstrip() for col in input_df.columns]))
    input_df = input_df.rename(columns=mapping)
    cols = self._mko.dataspec['inputs']
    inputs = input_df[cols].to_numpy().tolist()
    n_samples = self._analysis_data['n_samples']
    
    return {
      "mko" : mko_data,
      "inputs": inputs,
      "n_samples" : n_samples
    }
  
  def return_contents(self):
    if not self.ready:
      raise Exception("Not ready")

    string = json.loads(self.contents)['outputs']
    stream = StringIO(string)
    samples = np.loadtxt(stream)
    mean = samples.mean()
    std = samples.std()
    return mean, std, samples
  
  def format_contents_as_string(self):
    if not self.ready:
      raise Exception("Not ready")

    string = json.loads(self.contents)['outputs']
    stream = StringIO(string)
    samples = np.loadtxt(stream, delimiter=",")
    mean = samples.mean(axis=0)
    std = samples.std(axis=0)

    output = f"""
     Mean = {mean}
     STDDEV = {std}
     SAMPLES:
     {string} """

    return output

  def display_in_window(self):
    window = sg.Window("SAMPLES",
      [
        [ sg.Text("SAMPLES:", enable_events=False), ],
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
