import PySimpleGUI as sg
from bda_service.analyses import describe
from bdaInfer.analysisUIs import AnalysisUI

class DescribeUI(AnalysisUI):

  go_tag = "-DESCRIBE_GO-"
  analysis_data = {}
  name = "description"

  layout = [
    [
      sg.Text("DESCRIBE CONTENTS", font = ("Times", 13, "bold"))
    ],
    [
      sg.Text("analysis name:"), sg.In("description", size=10, enable_events=True, key="-DESCRIBE_NAME-")
    ],
    [
      sg.B("GO!", enable_events=True, key="-DESCRIBE_GO-")
    ]
  ]

  @classmethod
  def clear_data(cls):
    cls.analysis_data = {}

  @classmethod
  def handler(cls, event, values, window):

    if event== "-DESCRIBE_NAME-":
      cls.name = values["-DESCRIBE_NAME-"]
    if event == "-DESCRIBE_GO-":
      return False

