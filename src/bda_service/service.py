from datetime import datetime, timedelta
from logging import exception
import requests
import json
from bda_service.user import User
from bda_service.mko import MKO
from footer import statusbar

class BDAServiceException(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)
    pass

class BDAService(object):

  def __init__(self, baseurl: str, secret: str, admin : User):
    self._baseurl = baseurl
    self._secret = secret
    self._admin = admin
    self._access_list = ['user', 'admin', 'train', 'infer', 'analyze', 'logs']
  
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
    params = {
      "username": self.admin.username,
      "password": self.admin.password,
      "server_secret": self.secret
    }
    try:
      response = requests.get(self.baseurl + "/Admin/Init", params=params)
    except Exception as err:
      statusbar.update("Problems initializing server: {}".format(err))
      return

    statusbar.update("Service is init with code {}".format(response.status_code))

  def set_current_user(self, user):
    self._current_user = user

  @property
  def current_user(self):
    return self._current_user

  #### SERVICE OPERATIONS ####
  def redeem_claim_check(self, user: User, claim_check : str):
    url = self.baseurl + "/Results/get_result"
    data = user.params
    data = {"username" : user.username}
    data['claim_check'] = claim_check
    response = requests.get(url, headers=user.headers, params=data)
    print(response.content)
    return json.loads(response.content)['contents']

  def get_claim_check_status(self, user: User,  claim_check: str) -> float:
    url = self.baseurl + "/Results/get_status"
    data = {"username" : user.username }
    data['claim_check'] = claim_check
    response = requests.get(url, headers=user.headers, params=data)
    return float(response.content)

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

    try:
      response = requests.post(login_url, data=u.params, headers=u.headers)
      data = json.loads(response.content)
      auth_token = data['token']
      refresh_token = response.cookies['refresh_token']
      u.set_auth_token(auth_token)
      u.set_server(self)
      u.set_refresh_token(refresh_token)
    except Exception as err:
      statusbar.update("Could not login {} on server: {}".format(u.username, err))
      return
    statusbar.update("logged {} in on BDA server".format(u.username))

  def refresh_user_token(self, u: User):
    refresh_url = self.baseurl + "/User/refreshToken"
    response = requests.get(refresh_url, headers=u.headers, cookies=u.cookies)
    data = json.loads(response.content)
    auth_token = data['token']
    refresh_token = response.cookies['refresh_token']
    u.set_auth_token(auth_token)
    u.set_refresh_token(refresh_token)
  
  #### OPERATIONS ON MKOS ####
  def register_mko(self, mko : MKO):
    url = self.baseurl + "/Train/create_MKO"
    data = {"username": mko.user.username}
    data['model_name'] = mko.name
    data = json.dumps({'data' : data})
    response = requests.post(url, headers=mko.user.headers, data=data)
    claim_check = json.loads(response.content)['claim_check']
    mko._inprocess = True
    mko.set_progress(0.0)
    return claim_check

  def attach_data_to_mko(self, mko):
    url = self.baseurl + "/Train/fill_mko"
    data = {"username": mko.user.username}
    data['model_name'] = mko.name
    data['dataspec'] = mko.dataspec
    data['mkodata'] = mko.contents
    data = json.dumps({'data' : data})
    response = requests.post(url, headers=mko.user.headers, data=data)
    claim_check = json.loads(response.content)['claim_check']
    mko._inprocess = True
    mko.set_progress(0.0)
    return claim_check

  def train_mko(self, mko):
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
      except:
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
      if mko.stage == 0:
        claim_check = self.register_mko(mko)
        mko.set_claim_check(claim_check)
      if mko.stage == 1:
        claim_check = self.attach_data_to_mko(mko)
        mko.set_claim_check(claim_check)
      elif mko.stage == 2:
        claim_check = self.train_mko(mko)
        mko.set_claim_check(claim_check)