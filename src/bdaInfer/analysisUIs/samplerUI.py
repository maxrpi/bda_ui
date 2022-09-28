import PySimpleGUI as sg
from bda_service.analyses import sampler
from bdaInfer.analysisUIs import AnalysisUI

class SamplerUI(AnalysisUI):

  go_tag = "-SAMPLER_GO-"
  analysis_data = {}
  name = "default"

  layout = [
    [
      sg.Text("SAMPLE DIRECTLY", font = ("Times", 13, "bold"))
    ],
    [
      sg.Text("analysis name:"), sg.In(name, size=10, enable_events=True, key="-SAMPLER_NAME-")
    ],
    [
      sg.T("number of samples"), sg.In("", size=9, k="-SAMPLER_N_SAMPLES-", enable_events=True)
    ],
    [
      sg.In("", visible=False, enable_events=True, key="-SAMPLER_INPUT_FILENAME-"),
      sg.FileBrowse("Load Inputs",
        file_types=[('.csv','*.csv'),('.txt','*.txt')],
        key='-LOAD_SAMPLER_INPUTS-',
        enable_events=True)
    ],
    [
      sg.B("GO!", enable_events=True, key="-SAMPLER_GO-")
    ]
  ]

  @classmethod
  def clear_data(cls):
    cls.analysis_data = {}

  @classmethod
  def handler(cls, event, values, window):

    if event== "-SAMPLER_NAME-":
      cls.name = values["-SAMPLER_NAME-"]
    if event == "-SAMPLER_INPUT_FILENAME-":
      cls.analysis_data['input_filename'] = values["-SAMPLER_INPUT_FILENAME-"]
      return True
    if event == "-SAMPLER_N_SAMPLES-":
      cls.analysis_data['n_samples'] = values["-SAMPLER_N_SAMPLES-"]
      return True
    if event == "-SAMPLER_GO-":
      return False

