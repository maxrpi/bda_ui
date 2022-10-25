from datetime import datetime, timedelta
import copy
import jwt

class MKO(object):

  def __init__(
              self,
              name : str,
              user,
              service,
              series_type : str = "time",
              auto_progress : bool = True
              ) -> None:

    self._name : str = name
    self._user = user
    self._service = service
    self._series_type = series_type
    self._dataspec = {}
    self._topology = []
    self._hypers = {}
    self._stage : int = 0
    self._inprocess : bool = False
    self._progress : float = 0.0
    self._auto_progress = auto_progress
    self._unqueue = False
    self._error_count = 0
    self._time_as_input = False
    self._autocalibrate = False

  def copy(self, name):
    tmp = copy.deepcopy(self)
    tmp._user = self._user
    tmp._service = self._service
    tmp._name = name
    return tmp

  @property
  def name(self) -> str:
    return self._name

  @property
  def user(self):
    return self._user
  
  @property
  def lot_series(self):
    return self._series_type.lower() == "lot"

  @property
  def timeseries(self):
    return self._series_type.lower() == "time"

  def set_inputs_and_outputs_ts(self, inputs, outputs, time_as_input=False):
    assert(self.timeseries)
    self._inputs = inputs
    self._outputs = outputs
    self._time_as_input = time_as_input
  
  def set_inputs_and_outputs_ls(self, attrib_id, inputs, outputs):
    assert(self.lot_series)
    self._attrib_id = attrib_id
    self._inputs = inputs
    self._outputs = outputs
  
  def set_topology(self, topology):
    self._topology = topology

  def set_hypers(self, hypers):
    self._hypers = hypers
  
  def set_autocalibrate(self, autocalibrate=True):
    self._autocalibrate = autocalibrate

  def set_smip_auth(self, smip_auth):
    assert(len(smip_auth) > 0)
    self._smip_auth = smip_auth

  def set_time_parameters( self, start_time : datetime, end_time : datetime, 
    period : int, max_samples : int=0):
    assert(self.timeseries)
    self._start_time : datetime = start_time
    self._end_time : datetime = end_time
    self._period : int = period
    self._max_samples : int = max_samples

  def set_lot_parameters( self, all_lots, start_lot="",  end_lot=""):
    assert(self.lot_series)
    self._all_lots = all_lots
    self._start_lot = start_lot
    self._end_lot = end_lot

  def incorporate_dataspec(self, data):
    self._inputs = data['inputs']
    self._outputs = data['outputs']
    self._series_type = data['series_type']
    if self._series_type == "lot":
      self._attrib_id = data['query_json']['attrib_id']
      self._all_lots = data['query_json']['all_lots']
      self._start_lot = data['query_json']['start_lot']
      self._end_lot = data['query_json']['end_lot']
    else:
      self._start_time = data['query_json']['start_time']
      self._end_time = data['query_json']['end_time']
      self._period = data['query_json']['period']
      self._max_samples = data['query_json']['max_samples']
    self._time_as_input = data['time_as_input']
    self._smip_auth = {"url": data['data_location']}


  def generate_dataspec(self):
    self._dataspec =  {
      "series_type" : self._series_type,
      "inputs" : [str(tag) for tag in self._inputs],
      "outputs" : [str(tag) for tag in self._outputs],
      "data_location": self.smip_auth['url'],
      "query_json": {}
    }
    if self.lot_series:
      self._dataspec['attrib_id'] = self._attrib_id
      self._dataspec['query_json'].update({"all_lots" : self._all_lots })
      if self._all_lots:
        self._dataspec['query_json'].update({
          "start_lot" : self._start_lot,
          "end_lot" : self._end_lot
          })
    elif self.timeseries:
      self._dataspec['time_as_input'] = self._time_as_input
      self._dataspec['query_json'].update({
        "start_time": self._start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "end_time" : self._end_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "period" : self._period,
        "max_samples" : self._max_samples
        })
    else:
      raise Exception("This can't happen")
  

  @property
  def smip_auth(self):
    return self._smip_auth

  @property
  def dataspec(self):
    self.generate_dataspec()
    return self._dataspec

  @property
  def topology(self):
    return self._topology

  @property
  def hypers(self):
    return self._hypers
  
  @property
  def autocalibrate(self):
    return self._autocalibrate
  
  def set_claim_check(self, claim_check):
    self._claim_check = claim_check
    self.update_eta()

  def set_stage(self, stage):
    self._stage = stage

  @property
  def stage(self):
    return self._stage

  def set_inprocess(self, inprocess :bool):
    self._inprocess = inprocess
  
  @property
  def inprocess(self) -> bool:
    return self._inprocess

  def set_progress(self, progress : float):
    self._progress = progress
  
  def progress_stage(self):
    self._stage += 1
    self._progress = 0.0
    self._inprocess = False
  
  @property
  def progress(self) -> float:
    return self._progress
  
  @property
  def ready(self) -> bool:
    return self._stage == 3

  @property
  def too_many_errors(self):
    return self._error_count > 10

  def increment_error_counter(self):
    self._error_count += 1

  def reset_error_counter(self, count=0):
    self._error_count = count

  @property
  def claim_check(self):
    return self._claim_check

  def update_eta(self, eta=None):
    if eta == None:
      self._eta = datetime.fromtimestamp(
          float(jwt.decode(self.claim_check, options={"verify_signature": False})['eta'])
      )
    else:
      self._eta = eta

  @property
  def eta(self):
    return self._eta

  def set_contents(self, contents):
    self._contents = contents

  @property
  def contents(self):
    return self._contents

  def save_to_file(self, filename):
    with open(filename, "w", encoding="utf-8") as fd:
      fd.write(self.contents)
    return

  def load_from_file(self, filename):
    with open(filename, "r", encoding="utf-8") as fd:
      self.set_contents(fd.read())
    return

  def due(self, padding=0, forced=False):
    if forced or self._eta + timedelta(seconds=padding) < datetime.now():
      return True
    else:
      return False

  def refresh(self):
    if self._service is not None:
      self._service.refresh_mko(self)

  @property
  def auto_progress(self):
    return self._auto_progress

  def set_autoprogress(self, state=True):
    self._auto_progress = state

  def set_unqueue(self, state=True):
    self._unqueue = state

  @property
  def unqueue(self):
    return self._unqueue
