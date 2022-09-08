import PySimpleGUI as sg

from bda_service.analyses import Analysis

class Histogram(Analysis):
  def __init__(self, mko, n_samples, input_data) -> None:
    super().__init__("histogram", mko, n_samples, input_data)
    self._endpoint = "/Analyze/histogram"
    pass

  @property
  def endpoint(self):
    return self._endpoint

