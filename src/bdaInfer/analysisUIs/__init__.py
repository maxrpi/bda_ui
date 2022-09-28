
from bdaInfer.analysisUIs.analysisUIs import AnalysisUI
from bdaInfer.analysisUIs.cloudplotUI import CloudplotUI
from bdaInfer.analysisUIs.describeUI import DescribeUI
from bdaInfer.analysisUIs.histogramUI import HistogramUI
from bdaInfer.analysisUIs.integrationUI import IntegrationUI
from bdaInfer.analysisUIs.samplerUI import SamplerUI
from bdaInfer.analysisUIs.statisticsUI import StatisticsUI

UIs = {
  "sampler": SamplerUI,
  "histogram" : HistogramUI,
  "cloudplot" : CloudplotUI,
  "describe" : DescribeUI,
  "integration" : IntegrationUI,
  "statistics" : StatisticsUI,
}
