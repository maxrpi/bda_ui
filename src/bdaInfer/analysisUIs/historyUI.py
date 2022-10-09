import PySimpleGUI as sg
from bda_service.analyses import history
from bdaInfer.analysisUIs import AnalysisUI

class HistoryUI(AnalysisUI):

  go_tag = "-HISTORY_GO-"
  analysis_data = {}
  name = "history"

  layout = [
    [
      sg.Text("TRAINING HISTORY", font = ("Times", 13, "bold"))
    ],
    [
      sg.Text("analysis name:"), sg.In("history", size=10, enable_events=True, key="-HISTORY_NAME-")
    ],
    [
      sg.B("GO!", enable_events=True, key="-HISTORY_GO-")
    ]
  ]

  @classmethod
  def clear_data(cls):
    cls.analysis_data = {}

  @classmethod
  def handler(cls, event, values, window):

    if event== "-HISTORY_NAME-":
      cls.name = values["-HISTORY_NAME-"]
    if event == "-HISTORY_GO-":
      return False

