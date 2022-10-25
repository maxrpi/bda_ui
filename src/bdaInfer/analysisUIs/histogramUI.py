import PySimpleGUI as sg
from bdaInfer.analysisUIs import AnalysisUI

class HistogramUI(AnalysisUI):

  go_tag = "-HISTOGRAM_GO-"
  analysis_data = {}
  name = "hist"

  layout = [
    [
      sg.Text("CREATE HISTOGRAM", font = ("Times", 13, "bold")),
    ],
    [
      sg.Text("analysis name:"), sg.In(name, size=10, enable_events=True, key="-HISTOGRAM_NAME-")
    ],
    [
      sg.T("number of samples"), sg.In("", size=9, k="-HISTOGRAM_N_SAMPLES-", enable_events=True),
      sg.T("number of bins"), sg.In("", size=9, k="-HISTOGRAM_N_BINS-", enable_events=True),
    ],
    [
      sg.FileBrowse("Load Inputs",
        file_types=[('.csv','*.csv'),('.txt','*.txt')],
        key='-LOAD_HISTOGRAM_INPUTS-',
        enable_events=True,
        target="-HISTOGRAM_INPUT_FILENAME-"),
      sg.In("", visible=True, enable_events=True, key="-HISTOGRAM_INPUT_FILENAME-"),
    ],
    [
      sg.B("GO!", enable_events=True, key="-HISTOGRAM_GO-")
    ]
  ]


  @classmethod
  def handler(cls, event, values, window):

    if event== "-HISTOGRAM_NAME-":
      cls.name = values["-HISTOGRAM_NAME-"]
    if event == "-HISTOGRAM_INPUT_FILENAME-":
      cls.analysis_data['input_filename'] = values["-HISTOGRAM_INPUT_FILENAME-"]
      return True
    if event == "-HISTOGRAM_N_BINS-":
      cls.analysis_data['n_bins'] = values["-HISTOGRAM_N_BINS-"]
      return True
    if event == "-HISTOGRAM_N_SAMPLES-":
      cls.analysis_data['n_samples'] = values["-HISTOGRAM_N_SAMPLES-"]
      return True
    if event == "-HISTOGRAM_GO-":
      return False

