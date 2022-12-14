from bda_service.analyses.analysis import Analysis
from bda_service.analyses.describe import Describe
from bda_service.analyses.sampler import Sampler
from bda_service.analyses.cloudplot import Cloudplot
from bda_service.analyses.histogram import Histogram
from bda_service.analyses.history import History
from bda_service.analyses.integration import Integration
from bda_service.analyses.statistics import Statistics

analysis_types = {
  "sampler" : Sampler,
  "histogram": Histogram,
  "cloudplot" : Cloudplot,
  "describe" : Describe,
  "integration" : Integration,
  "history" : History,
}