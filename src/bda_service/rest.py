from datetime import datetime, timedelta
from wsgiref import validate
import requests
import json
import jwt

class User(object):
  def __init__(self, username, password, email=""):
    self._username = username
    self._password = password
    self._email = email
    self._auth_token = ""
    self._refresh_token = ""
    self._server = ""
    self.refresh_lifetime = 600

  @property
  def username(self) -> str:
    return self._username

  @property
  def password(self) -> str:
    return self._password

  @property
  def email(self) -> str:
    return self._email
  
  @property
  def auth_token(self) -> str:
    return self._auth_token

  @property
  def refresh_token(self) -> str:
    return self._refresh_token

  @property
  def server(self):
    return self._server
  
  @property
  def params(self):
    params = {
      "username": self.username,
      "password": self.password
    }
    return params

  @property
  def headers(self):
    headers = {
      "Authorization": "Bearer {}".format(self.auth_token),
    }
    return headers

  @property
  def cookies(self):
    headers = {
      "refresh_token": format(self.refresh_token),
    }
    return headers

  def __eq(self, other):
    return self.username == other.username

  def __hash__(self):
    return hash(self.username)

  def set_auth_token(self, auth_token):
    self._auth_token = auth_token
    self._auth_dict = jwt.decode(self.auth_token, options={"verify_signature":False})


  def set_refresh_token(self, refresh_token):
    self._refresh_time = datetime.now() + timedelta(seconds=self.refresh_lifetime)
    self._refresh_token = refresh_token
    self._auth_dict = jwt.decode(self.refresh_token, options={"verify_signature":False})

  @property
  def refresh_expiration(self):
    return datetime.fromtimestamp(self._refresh_dict.get('expiration_date')).strftime("%m/%d/%Y, %H:%M:%S")

  @property
  def auth_expiration(self):
    return datetime.fromtimestamp(self._auth_dict.get('expiration_date')).strftime("%m/%d/%Y, %H:%M:%S")

  def set_server(self, server):
    self._server = server

  def due(self) -> bool:
    now = datetime.now()
    if now > self._refresh_time:
      return True
    else:
      return False

  def refresh(self, forced=False):
    if self.due() or forced == True:
      self.server.refresh_token(self)

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
  

def create_mko(server:BDAService, user:User, model_name:str):
  url = server.baseurl + "/Train/create_MKO"
  data = user.params
  data['model_name'] = model_name
  response = requests.post(url, headers=user.headers, data=data)

  claim_check = json.loads(response.content)['claim_check']
  return claim_check

def redeem_claim_check(server: BDAService, user: User, claim_check : str):
  url = server.baseurl + "/Results/get_result"
  data = user.params
  data['claim_check'] = claim_check
  response = requests.get(url, headers=user.headers, params=data)
  print(response.content)
  return response.content
