import PySimpleGUI as sg
from bdaInfer.analysisUIs import AnalysisUI

class IntegrationUI(AnalysisUI):

  go_tag = "-INTEGRATION_GO-"
  analysis_data = {}
  name = "default"

  layout = [
    [
      sg.Text("INTEGRATE FUNCTION", font = ("Times", 13, "bold")),
    ],
    [
      sg.Text("analysis name:"), sg.In(name, size=10, enable_events=True, key="-INTEGRATION_NAME-")
    ],
    [
      sg.T("number of samples"), sg.In("", size=9, k="-INTEGRATION_N_SAMPLES-", enable_events=True),
    ],
    [
      sg.In("", visible=False, enable_events=True, key="-INTEGRATION_INPUT_FILENAME-"),
      sg.FileBrowse("Load Inputs",
        file_types=[('.txt','*.txt')],
        key='-LOAD_INTEGRATION_INPUTS-',
        enable_events=True)
    ],
    [
      sg.In("", visible=False, enable_events=True, key="-INTEGRATION_FUNCTION_FILENAME-"),
      sg.FileBrowse("Load Function Table",
        file_types=[('.txt','*.txt')],
        key='-LOAD_INTEGRATION_FUNCTION-',
        enable_events=True)
    ],
    [
      sg.B("GO!", enable_events=True, key="-INTEGRATION_GO-")
    ]
  ]


  @classmethod
  def handler(cls, event, values, window):

    if event== "-INTEGRATION_NAME-":
      cls.name = values["-INTEGRATION_NAME-"]
    if event == "-INTEGRATION_INPUT_FILENAME-":
      cls.analysis_data['input_filename'] = values["-INTEGRATION_INPUT_FILENAME-"]
      return True
    if event == "-INTEGRATION_FUNCTION_FILENAME-":
      cls.analysis_data['function_filename'] = values["-INTEGRATION_FUNCTION_FILENAME-"]
      return True
    if event == "-INTEGRATION_N_SAMPLES-":
      cls.analysis_data['n_samples'] = values["-INTEGRATION_N_SAMPLES-"]
      return True
    if event == "-INTEGRATION_GO-":
      return False

