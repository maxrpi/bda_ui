from datetime import datetime, timedelta
import jwt
from bda_service.service import BDAService

class MKO(object):

  def __init__(self, name, user, service) -> None:
    self._name = name
    self._user = user
    self._service = service
    self._status = -1
    self._stage = 0

  def set_dataspec(self, inputs, outputs, start_time, end_time, period, max_samples=0):
    self._dataspec = {
      "x_tags" : [str(tag) for tag in inputs],
      "y_tags" : [str(tag) for tag in outputs],
      "query_json": {
        "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "end_time" : end_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "period" : period,
        "max_samples" : max_samples
      }
    }
    self._inputs = inputs
    self._outputs = outputs
    self._start_time = start_time
    self._end_time = end_time
    self._period = period
    self._max_samples = max_samples
  
  def set_status(self, status):
    self._status = status

  def update_eta(self, eta=None):
    if eta == None:
      self._eta = datetime.fromtimestamp(
          jwt.decode(self.claim_check, options={"verify_signature": False})['eta']
      )
    else:
      self._eta = eta
    

  def set_claim_check(self, claim_check):
    self._claim_check = claim_check
    self.update_eta()

  def set_stage(self, stage):
    self._stage = stage

  @property
  def stage(self):
    return self._stage

  @property
  def eta(self):
    return self._eta

  @property
  def claim_check(self):
    return self._claim_check

  @property
  def status(self):
    return self._status
  
  def due(self, padding=0, forced=False):
    if forced or self._eta + timedelta(seconds=padding) < datetime.now():
      return True
    else:
      return False

  def refresh(self):
    self._service.refresh_mko(self)

  def update_status(self):
    try:
      if self._status > 1.0:
        return
      status = self._service.get_status(self._user, self._claim_check)
      self.set_status(status)
    except:
      return

  def redeem(self):
    """ Don't use. Breaks model for direction of information flow"""
    try:
      data = self._service.redeem_claim_check(self._user, self._claim_check)
      self._data = data
      self._stage += 1
      self._status = -1
    except:
      return
  