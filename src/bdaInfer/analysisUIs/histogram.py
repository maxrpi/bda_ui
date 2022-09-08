import PySimpleGUI as sg
from bdaInfer.analysisUIs import AnalysisUI

class HistogramUI(AnalysisUI):

  go_tag = "-HISTOGRAM_GO-"
  analysis_data = {}

  layout = [
    [
      sg.Text("CREATE HISTOGRAM", font = ("Times", 13, "bold"))
    ],
    [
      sg.T("number of samples"), sg.In("", size=9, k="-HISTOGRAM_N_SAMPLES-", enable_events=True)
    ],
    [
      sg.In("", visible=False, enable_events=True, key="-HISTOGRAM_INPUT_FILENAME-"),
      sg.FileBrowse("Load Inputs",
        file_types=[('.txt','*.txt')],
        key='-LOAD_HISTOGRAM_INPUTS-',
        enable_events=True)
    ],
    [
      sg.B("GO!", enable_events=True, key="-HISTOGRAM_GO-")
    ]
  ]


  @classmethod
  def handler(cls, event, values, window):

    if event == "-HISTOGRAM_INPUT_FILENAME-":
      cls.analysis_data['input_filename'] = values["-HISTOGRAM_INPUT_FILENAME-"]
      return True
    if event == "-HISTOGRAM_N_SAMPLES-":
      cls.analysis_data['n_samples'] = values["-HISTOGRAM_N_SAMPLES-"]
      return True
    if event == "-HISTOGRAM_GO-":
      return False

