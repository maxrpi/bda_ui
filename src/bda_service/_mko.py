from datetime import datetime, timedelta
import profile
import jwt
import json

class MKO(object):

  def __init__(
              self,
              name : str,
              user,
              service,
              auto_progress : bool = True
              ) -> None:

    self._name : str = name
    self._user = user
    self._service = service
    self._dataspec = {}
    self._stage : int = 0
    self._inprocess : bool = False
    self._progress : float = 0.0
    self._auto_progress = auto_progress
    self._unqueue = False
    self._error_count = 0

  @property
  def name(self) -> str:
    return self._name

  @property
  def user(self):
    return self._user

  def set_inputs_and_outputs(self, inputs, outputs):
    self._inputs = inputs
    self._outputs = outputs
  
  def set_smip_auth(self, smip_auth):
    self._smip_auth = smip_auth

  def set_time_parameters( self, start_time : datetime, end_time : datetime, 
    period : int, max_samples : int=0):

    self._start_time : datetime = start_time
    self._end_time : datetime = end_time
    self._period : int = period
    self._max_samples : int = max_samples

  def generate_dataspec(self):
    self._dataspec =  {
      "x_tags" : [str(tag) for tag in self._inputs],
      "y_tags" : [str(tag) for tag in self._outputs],
      "n_inputs": len(self._inputs),
      "n_outputs": len(self._outputs),
      "data_location": self.smip_auth['url'],
      "query_json": {
        "start_time": self._start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "end_time" : self._end_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "period" : self._period,
        "max_samples" : self._max_samples
      }
    }
  
  @property
  def smip_auth(self):
    return self._smip_auth

  @property
  def dataspec(self):
    self.generate_dataspec()
    return self._dataspec
  
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

  def set_unqueue(self, state=True):
    self._unqueue = state

  @property
  def unqueue(self):
    return self._unqueue

  """ Don't use. Breaks model for direction of information flow"""
  def redeem(self):
    try:
      data = self._service.redeem_claim_check(self._user, self._claim_check)
      self._data = data
      self._stage += 1
      self._status = -1
    except:
      return
  