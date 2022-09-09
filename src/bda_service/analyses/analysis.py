from datetime import datetime
import jwt

class Analysis(object):
  def __init__(
        self,
        name, analysis_type,
        mko, service,
        analysis_data,
        ) -> None:
    self._name = name
    self._analysis_type = analysis_type
    self._mko = mko
    self._analysis_data, = analysis_data,

    self._direct_response = False
    self._inprocess = False
    self._progress = 0.0
    self._claim_check = ""
    self._service = service
    self._contents = None
    self._ready = False
    self._unqueue = False
    self._endpoint = NotImplemented

  ##### PURE VIRTUAL METHODS #####
  
  def query_data(self) -> dict:
    raise NotImplemented

  def return_contents(self):
    raise NotImplemented

  ##### Implemented methods #####

  @property
  def name(self):
    return self._name

  @property
  def endpoint(self) -> str:
    return self._endpoint

  def set_progress(self, progress : float):
    self._progress = progress

  def set_claim_check(self, claim_check : str):
    self._claim_check = claim_check
    self.update_eta()
  
  def reset_error_counter(self, counter : int=0):
    self._error_counter = counter

  def increment_error_counter(self):
    self._error_counter += 1

  @property
  def too_many_errors(self) -> bool:
    return self._error_counter > 10

  def set_contents(self, contents):
    self._contents = contents

  @property
  def contents(self):
    return self._contents
  
  def refresh(self):
    if self._service is not None:
      self._service.refresh_analysis(self)

  def set_unqueue(self, state=True):
    self._unqueue = state

  @property
  def unqueue(self):
    return self._unqueue

  @property
  def user(self):
    return self._service.current_user

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
  
  @property
  def ready(self):
    return self._ready

  @property
  def direct_response(self):
    return self._direct_response

  def set_ready(self, state=True):
    self._ready = state

  @property
  def progress(self):
    return self._progress

  @property
  def inprocess(self):
    return self._inprocess