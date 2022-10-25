import PySimpleGUI as sg

from bda_service.analyses import Analysis

class Statistics(Analysis):
  def __init__(self, name, mko, service, analysis_data) -> None:
    super().__init__(name,"statistics", mko, service, analysis_data)
    self._endpoint = "/Analyze/statistics"
    pass

  @property
  def endpoint(self):
    return self._endpoint

