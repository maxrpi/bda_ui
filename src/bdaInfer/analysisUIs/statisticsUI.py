import PySimpleGUI as sg
from bda_service.analyses import sampler
from bdaInfer.analysisUIs import AnalysisUI

class StatisticsUI(AnalysisUI):

  go_tag = "-STATISTICS_GO-"
  analysis_data = {}

  layout = [
    [
      sg.Text("CREATE STATISTICS", font = ("Times", 13, "bold"))
    ],
    [
      sg.T("number of samples"), sg.In("", size=9, k="-STATISTICS_N_SAMPLES-", enable_events=True)
    ],
    [
      sg.In("", visible=False, enable_events=True, key="-STATISTICS_INPUT_FILENAME-"),
      sg.FileBrowse("Load Inputs",
        file_types=[('.txt','*.txt')],
        key='-LOAD_STATISTICS_INPUTS-',
        enable_events=True)
    ],
    [
      sg.B("GO!", enable_events=True, key="-STATISTICS_GO-")
    ]
  ]


  @classmethod
  def handler(cls, event, values, window):

    if event == "-STATISTICS_INPUT_FILENAME-":
      cls.analysis_data['input_filename'] = values["-STATISTICS_INPUT_FILENAME-"]
      return True
    if event == "-STATISTICS_N_SAMPLES-":
      cls.analysis_data['n_samples'] = values["-STATISTICS_N_SAMPLES-"]
      return True
    if event == "-STATISTICS_GO-":
      return False

