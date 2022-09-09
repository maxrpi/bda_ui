import PySimpleGUI as sg
import numpy as np
import json
from io import StringIO

from support_functions import encodings
from bda_service.analyses import Analysis

class Histogram(Analysis):
  def __init__(self, name, mko, service, analysis_data) -> None:
    super().__init__(name,"histogram", mko, service, analysis_data)
    self._endpoint = "/Analyze/histogram"
    self._direct_response = False

  def query_data(self) -> dict:
    mko_data = self._mko.contents
    inputs = np.loadtxt(self._analysis_data['input_filename']).tolist()
    n_samples = self._analysis_data.get('n_samples', "0")
    n_bins = self._analysis_data.get('n_bins', "0")
    try: int(n_bins)
    except: n_bins = 0
    try: int(n_samples)
    except: n_samples = 0
    
    return {
      "mko" : mko_data,
      "inputs": inputs,
      "n_samples" : n_samples,
      "n_bins" : n_bins,
    }
  
  def return_contents(self):
    if not self.ready:
      raise Exception("Not ready")
    return self._contents
    
  
  def return_contents_as_image(self):
    if not self.ready:
      raise Exception("Not ready")

    image = encodings.decode_base64(self.contents)
    return image

  def display_in_window(self):
    window = sg.Window("SAMPLES",
      [
        [ sg.Text("SAMPLES:", enable_events=False), ],
        [
          sg.B("SAVE", enable_events=True, key="-SAVEAS-"), 
          sg.B("EXIT", enable_events=True, key="-EXIT-")
        ],
        [ sg.Image(key="-IMAGE_BOX-", size=(500,500) ) ],
      ]
    , finalize=True, size=(510,600))
    
    image = self.return_contents_as_image()
    window['-IMAGE_BOX-'].update(data=image)

    while True:
      event, values = window.read()
      if event == sg.WINDOW_CLOSED or event == "-EXIT-":
        break
    window.close()