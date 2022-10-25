import PySimpleGUI as sg
import numpy as np
import json
import pandas as pd
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
    input_df = pd.read_csv(self._analysis_data['input_filename'])
    mapping =  dict(zip(input_df.columns, [ col.lstrip().rstrip() for col in input_df.columns]))
    input_df = input_df.rename(columns=mapping)
    cols = self._mko.dataspec['inputs']
    inputs = encodings.b64encode_datatype(input_df[cols].to_numpy()[0])
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

    coded_images = encodings.b64decode_datatype(self.contents)
    return [ encodings.decode_base64(image)  for image in coded_images ]

  def display_in_window(self):
    window = sg.Window("HISTOGRAM",
      [
        [ sg.Text("HISTOGRAM:", enable_events=False), ],
        [
          sg.B("PREVIOUS", enable_events=True, key="-PREVIOUS-"), 
          sg.B("NEXT", enable_events=True, key="-NEXT-"), 
          sg.In("", visible=False, enable_events=True, key="-SAVE_FILENAME-"),
          sg.SaveAs("SAVE",
            key="-SAVEAS-", target="-SAVE_FILENAME-",
            default_extension=".png",
            file_types=[('PNG','*.png'), ('PNG','*.PNG')],
            initial_folder="data",
          ),
          sg.B("EXIT", enable_events=True, key="-EXIT-")
        ],
        [ sg.Image(key="-IMAGE_BOX-", size=(500,500) ) ],
      ]
    , finalize=True, size=(510,600))
    
    images = self.return_contents_as_image()
    n_images = len(images)
    index = 0
    index = index % n_images

    window['-IMAGE_BOX-'].update(data=images[index])

    while True:
      event, values = window.read()
      if event == sg.WINDOW_CLOSED or event == "-EXIT-":
        break
      if event == "-NEXT-":
        index = (index + 1) % n_images
        window['-IMAGE_BOX-'].update(data=images[index])
      if event == "-PREVIOUS-":
        index = (index + n_images - 1) % n_images
        window['-IMAGE_BOX-'].update(data=images[index])
      if event == "-SAVE_FILENAME-":
        filename = values["-SAVE_FILENAME-"]
        with open(filename, "wb") as fd:
          fd.write(images[index])
          fd.close()

    window.close() 