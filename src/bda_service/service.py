from datetime import datetime, timedelta
import requests
import json
from bda_service.user import User
from bda_service.mko import MKO


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

  def initialize_server(self):
    params = {
      "username": self.admin.username,
      "password": self.admin.password,
      "server_secret": self.secret
    }
    
    response = requests.get(self.baseurl + "/Admin/Init", params=params)
    print("Service is init with code {}".format(response.status_code))

  def add_user(self, u: User):
    params = {
      "username": u.username,
      "password": u.password,
      "email": u.email,
      "access_list": self._access_list
    }

    response = requests.post(self.baseurl + "/Admin/create_user",
      data=params, headers=self.admin.headers)
    
  
  def login_user(self, u: User):
    login_url = self.baseurl + "/User/getToken"

    response = requests.post(login_url, data=u.params, headers=u.headers)
    data = json.loads(response.content)
    auth_token = data['token']
    refresh_token = response.cookies['refresh_token']
    u.set_auth_token(auth_token)
    u.set_server(self)
    u.set_refresh_token(refresh_token)

  def refresh_token(self, u: User):
    print("User {} refreshing token".format(u.username))
    refresh_url = self.baseurl + "/User/refreshToken"

    response = requests.get(refresh_url, headers=u.headers, cookies=u.cookies)
     
    data = json.loads(response.content)
    auth_token = data['token']
    refresh_token = response.cookies['refresh_token']
    u.set_auth_token(auth_token)
    u.set_refresh_token(refresh_token)
  
  def register_mko(self, mko):
    url = self.baseurl + "/Train/create_MKO"
    data = mko.user.params
    data['model_name'] = mko.model_name
    response = requests.post(url, headers=mko.user.headers, data=data)
    claim_check = json.loads(response.content)['claim_check']
    return claim_check
  
  def attach_data(self, mko):
    url = self.baseurl + "/Train/fill_data"
    data = mko.user.params
    data['dataspec'] = mko.dataspec
    query={"query": data}
    response = requests.post(url, headers=mko.user.headers, data=query)
    claim_check = json.loads(response.content)['claim_check']
    return claim_check

  def train_mko(self, mko):
    url = self.baseurl + "/Train/train"
    data = mko.user.params
    data['mko'] = mko.data
    query={"query": data}
    response = requests.post(url, headers=mko.user.headers, data=query)
    claim_check = json.loads(response.content)['claim_check']
    return claim_check

  def refresh_mko(self, mko):
    if mko.stage == "ready":
      return "ready"
    
    if mko.status < 1.0:
      status = self.get_status(mko.user, mko.claim_check)
      mko.set_status(status)
  
  def progress_mko(self, mko):
    if mko.stage == 0:
      claim_check = self.register_mko(mko)
    elif mko.stage == 1:
      claim_check = self.attach_data(mko)
    elif mko.stage == 2:
      claim_check = self.train_mko(mko)
    else:
      return ""
    return claim_check

  def redeem_claim_check(self, user: User, claim_check : str):
    url = self.baseurl + "/Results/get_result"
    data = user.params
    data['claim_check'] = claim_check
    response = requests.get(url, headers=user.headers, params=data)
    print(response.content)
    return response.content

  def get_status(self, user,  claim_check: str):
    url = self.baseurl + "/Results/get_status"
    data = user.params
    data['claim_check'] = claim_check
    response = requests.get(url, headers=user.headers, params=data)
    print(response.content)
    return response.content
