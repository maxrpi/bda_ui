import PySimpleGUI as sg
from bdaInfer.analysisUIs import AnalysisUI

class CloudplotUI(AnalysisUI):

  go_tag = "-CLOUDPLOT_GO-"
  analysis_data = {}
  name = "cloudplot"

  layout = [
    [
      sg.Text("CREATE CLOUDPLOT", font = ("Times", 13, "bold")),
    ],
    [
      sg.Text("analysis name:"), sg.In(name, size=10, enable_events=True, key="-CLOUDPLOT_NAME-")
    ],
    [
      sg.T("number of samples"), sg.In("", size=9, k="-CLOUDPLOT_N_SAMPLES-", enable_events=True),
    ],
    [
      sg.FileBrowse("Load Inputs",
        file_types=[('.csv','*.csv'),('.txt','*.txt')],
        key='-LOAD_CLOUDPLOT_DATA-',
        target="-CLOUDPLOT_DATA_FILENAME-",
        enable_events=True),
      sg.In("", visible=True, enable_events=True, key="-CLOUDPLOT_DATA_FILENAME-"),
    ],
    [
      sg.Checkbox("Errorbars", enable_events=True, key="-CLOUDPLOT_ERRORBARS-")
    ],
    [
      sg.B("GO!", enable_events=True, key="-CLOUDPLOT_GO-")
    ]
  ]


  @classmethod
  def handler(cls, event, values, window):

    if event== "-CLOUDPLOT_NAME-":
      cls.name = values["-CLOUDPLOT_NAME-"]
    if event == "-CLOUDPLOT_DATA_FILENAME-":
      cls.analysis_data['data_filename'] = values["-CLOUDPLOT_DATA_FILENAME-"]
      return True
    if event == "-CLOUDPLOT_N_SAMPLES-":
      cls.analysis_data['n_samples'] = values["-CLOUDPLOT_N_SAMPLES-"]
      return True
    if event == "-CLOUDPLOT_ERRORBARS-":
      cls.analysis_data['error_bars'] = values["-CLOUDPLOT_ERRORBARS-"]
      return True
    if event == "-CLOUDPLOT_GO-":
      return False

