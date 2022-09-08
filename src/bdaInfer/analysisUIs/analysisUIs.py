import abc

class AnalysisUI(abc.ABC):
  def __init__(self) -> None:
    pass

  @staticmethod
  def handler(event, values, window):
    pass
