
from bdaInfer.analysisUIs.analysisUIs import AnalysisUI
from bdaInfer.analysisUIs.cloudplotUI import CloudplotUI
from bdaInfer.analysisUIs.histogramUI import HistogramUI
from bdaInfer.analysisUIs.samplerUI import SamplerUI
from bdaInfer.analysisUIs.statistics import StatisticsUI

UIs = {
  "sampler": SamplerUI,
  "histogram" : HistogramUI,
  "cloudplot" : CloudplotUI
}
