import PySimpleGUI as sg
import numpy as np
import json
import pandas as pd
from io import StringIO

from support_functions import encodings
from bda_service.analyses import Analysis

class History(Analysis):
  def __init__(self, name, mko, service, analysis_data) -> None:
    super().__init__(name,"history", mko, service, analysis_data)
    self._endpoint = "/Analyze/history"
    self._direct_response = False

  def query_data(self) -> dict:
    mko_data = self._mko.contents
    
    return {
      "mkodata" : mko_data,
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
    window = sg.Window("Training History",
      [
        [ sg.Text("Training History:", enable_events=False), ],
        [
          sg.In("", visible=False, enable_events=True, key="-SAVE_FILENAME-"),
          sg.SaveAs("SAVE",
            key="-SAVEAS-", target="-SAVE_FILENAME-",
            default_extension=".png",
            file_types=[('PNG','*.png'), ('PNG','*.PNG')], initial_folder="data",
          ),
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
      if event == "-SAVE_FILENAME-":
        filename = values["-SAVE_FILENAME-"]
        with open(filename, "wb") as fd:
          fd.write(image)
          fd.close()

    window.close()