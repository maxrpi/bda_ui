import PySimpleGUI as sg
import numpy as np
import json

from bda_service.analyses import Analysis

class Describe(Analysis):
  def __init__(self, name, mko, service, analysis_data) -> None:
    super().__init__(name,"sampler", mko, service, analysis_data)
    self._endpoint = "/Train/describe_mko"
    self._direct_response = True

  def query_data(self) -> dict:
    mko_data = self._mko.contents
    
    return {
      "mkodata" : mko_data,
    }
  
  def format_contents_as_string(self):
    if not self.ready:
      raise Exception("Not ready")

    string = json.dumps(json.loads(self.contents), indent=2)

    return string

  def display_in_window(self):
    window = sg.Window("MKO",
      [
        [ sg.Text("MKO:", enable_events=False), ],
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
