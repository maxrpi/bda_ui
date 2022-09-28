from datetime import datetime, timedelta
from logging import exception
import requests
import json
from bda_service._user import User
from bda_service._mko import MKO
from bda_service.analyses import Analysis
from footer import statusbar

class BDAServiceException(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)
    pass
class ServiceNotInitialized(BDAServiceException):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)
    pass
class ServiceNotLoggedIn(BDAServiceException):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)
    pass

class BDAService(object):

  def __init__(self):
    self._baseurl : str
    self._secret  : str
    self._admin : User
    self._access_list : list
    self._initialized = False
    self._has_data = False
    self._smip_auth : dict
    self._current_user : User = None
  
  def set_data(self, baseurl: str, secret: str, admin : User):
    self._baseurl = baseurl
    self._secret = secret
    self._admin = admin
    self._access_list = ['user', 'admin', 'train', 'infer', 'analyze', 'logs']
    self._has_data = True
  
  def set_initialized(self, state=True):
    self._initialized = state

  @property
  def initialized(self):
    return self._initialized

  @property
  def baseurl(self) -> str:
    return self._baseurl
  
  @property
  def admin(self) -> User:
    return self._admin
  
  @property
  def secret(self) -> str:
    return self._secret

  #### SERVICE STATE FUNCTIONS ####
  def initialize_server(self):
    if not self._has_data:
      raise Exception("Cannot initialize empty server")
    params = {
      "username": self.admin.username,
      "password": self.admin.password,
      "server_secret": self.secret
    }
    response = requests.get(self.baseurl + "/Admin/Init", params=params)
    self.set_initialized()

  def set_current_user(self, user):
    self._current_user = user

  def set_baseurl(self, url):
    self._baseurl = url
  
  def set_smip_auth(self, url, username, role, password, smip_token):
    self._smip_auth = {
      "url"       : url,
      "username"  : username,
      "role"      : role,
      "password"  : password,
      "token": smip_token,
    }

  @property
  def current_user(self):
    try:
      return self._current_user
    except Exception as err:
      raise ServiceNotLoggedIn(err)

  @property
  def smip_auth(self):
    return self._smip_auth

  #### SERVICE OPERATIONS ####
  def redeem_claim_check(self, user: User, claim_check : str):
    url = self.baseurl + "/Results/get_result"
    data = user.params
    data = {"username" : user.username}
    data['claim_check'] = claim_check
    response = requests.get(url, headers=user.headers, params=data)
    return json.loads(response.content)['contents']

  def get_claim_check_status(self, user: User,  claim_check: str) -> float:
    url = self.baseurl + "/Results/get_status"
    data = {"username" : user.username }
    data['claim_check'] = claim_check
    response = requests.get(url, headers=user.headers, params=data)
    status = float(response.content)
    return status

  #### OPERATIONS ON USERS ####
  def add_user(self, u: User):
    params = {
      "username": u.username,
      "password": u.password,
      "email": u.email,
      "access_list": self._access_list
    }
    try:
      response = requests.post(self.baseurl + "/Admin/create_user",
        data=params, headers=self.admin.headers)
    except Exception as err:
      statusbar.update("Could not create user {} on server".format(u.username))
      return
    statusbar.update("User {} created on server".format(u.username))
    
  def login_user(self, u: User):
    login_url = self.baseurl + "/User/getToken"

    response = requests.post(login_url, data=u.params, headers=u.headers)
    data = json.loads(response.content)
    auth_token = data['token']
    refresh_token = response.cookies['refresh_token']
    u.set_auth_token(auth_token)
    u.set_server(self)
    u.set_refresh_token(refresh_token)
    u.set_logged_in(True)

  def refresh_user_token(self, u: User):
    refresh_url = self.baseurl + "/User/refreshToken"
    response = requests.get(refresh_url, headers=u.headers, cookies=u.cookies)
    data = json.loads(response.content)
    auth_token = data['token']
    refresh_token = response.cookies['refresh_token']
    u.set_auth_token(auth_token)
    u.set_refresh_token(refresh_token)
    statusbar.update(f"Refreshing user login for {u.username}")
  
  #### OPERATIONS ON MKOS ####
  def register_mko(self, mko : MKO):
    url = self.baseurl + "/Train/create_MKO"
    data = {"username": mko.user.username}
    data['model_name'] = mko.name
    data = json.dumps({'data' : data})
    response = requests.post(url, headers=mko.user.headers, data=data)
    if response.status_code != 200:
      mko.set_unqueue()
      raise Exception("Could not register MKO {}".format(mko.name))
    claim_check = json.loads(response.content)['claim_check']
    mko._inprocess = True
    mko.set_progress(0.0)
    return claim_check

  def attach_data_to_mko(self, mko):
    url = self.baseurl + "/Train/fill_mko"
    data = {"username": mko.user.username}
    data['model_name'] = mko.name
    data['dataspec'] = mko.dataspec
    data['topology'] = mko.topology
    data['hyper_parameters'] = mko.hypers
    data['mkodata'] = mko.contents
    data = json.dumps({'data' : data})
    response = requests.post(url, headers=mko.user.headers, data=data)
    claim_check = json.loads(response.content)['claim_check']
    mko._inprocess = True
    mko.set_progress(0.0)
    return claim_check

  def train_mko(self, mko : MKO):
    if mko.autocalibrate:
      url = self.baseurl + "/Train/trainCalibrate"
    else:
      url = self.baseurl + "/Train/train"
    data = {"username": mko.user.username}
    data['model_name'] = mko.name
    data['mkodata'] = mko.contents
    data['smip_auth'] = mko.smip_auth
    data = json.dumps({'data' : data})
    response = requests.post(url, headers=mko.user.headers, data=data)
    claim_check = json.loads(response.content)['claim_check']
    mko._inprocess = True
    mko.set_progress(0.0)
    return claim_check

  def refresh_mko(self, mko : MKO):

    if mko.inprocess == True:
      try:
        progress = self.get_claim_check_status(mko.user, mko.claim_check)
        mko.reset_error_counter()
      except:
        mko.increment_error_counter()
        if mko.too_many_errors:
          statusbar.update("Too many errors, bailing on MKO '{}'".format(mko.name))
          mko.set_unqueue()
        return

      mko.set_progress(progress)
      
      if progress >= 1.0:
        try:
          data = self.redeem_claim_check(mko.user, mko.claim_check)
          mko.set_contents(data)
        except:
          raise BDAServiceException("Could not redeem claim check")
        
        mko.progress_stage()
      else:
        return

    if mko.auto_progress and not mko.inprocess:
      try:
        if mko.stage == 0:
          claim_check = self.register_mko(mko)
          mko.set_claim_check(claim_check)
        if mko.stage == 1:
          claim_check = self.attach_data_to_mko(mko)
          mko.set_claim_check(claim_check)
        elif mko.stage == 2:
          claim_check = self.train_mko(mko)
          mko.set_claim_check(claim_check)
      except Exception as err:
        statusbar.update(err)

  def get_mko_as_dict(self, mko : MKO):
    data = {
      "mkodata" : mko.contents
    }
    data = json.dumps({'data' : data})
    url = self.baseurl + "/Train/describe_mko"
    response = requests.post(url, headers=self.current_user.headers, data=data)
    return json.loads(response.content)


  ##### OPERATIONS ON ANALYSES #####
  def launch_analysis(self, analysis : Analysis):
    url = self.baseurl + analysis.endpoint
    data = analysis.query_data()
    data.update({"username": self.current_user.username})
    data = json.dumps({'data' : data})
    if analysis.direct_response:
      response = requests.post(url, headers=self.current_user.headers, data=data)
      analysis.set_contents(response.content)
      analysis.set_ready()
      return
    response = requests.post(url, headers=self.current_user.headers, data=data)
    claim_check = json.loads(response.content)['claim_check']
    analysis._inprocess = True
    analysis.set_progress(0.0)
    analysis.set_claim_check(claim_check)


  def refresh_analysis(self, analysis : Analysis):

    if analysis._inprocess == True:
      try:
        progress = self.get_claim_check_status(analysis.user, analysis.claim_check)
        analysis.reset_error_counter()
      except:
        analysis.increment_error_counter()
        if analysis.too_many_errors:
          statusbar.update("Too many errors, bailing on analysis '{}'".format(analysis.name))
          analysis.set_unqueue()
        return

      analysis.set_progress(progress)
      
      if progress >= 1.0:
        try:
          data = self.redeem_claim_check(analysis.user, analysis.claim_check)
          analysis.set_contents(data)
          analysis.set_ready()
        except:
          raise BDAServiceException("Could not redeem claim check")
        
        