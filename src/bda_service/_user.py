from datetime import datetime, timedelta
import requests
import json
import jwt
user_id = 0


class User(object):
  def __init__(self, username, password, email=""):
    global user_id
    self.user_id = user_id
    user_id = user_id + 1
    self._username = username
    self._password = password
    self._email = email
    self._auth_token = ""
    self._refresh_token = ""
    self.refresh_lifetime = 600
    self._logged_in = False

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

  def __eq__(self, other):
    return self.username == other.username

  def __hash__(self):
    return hash(self.username)

  def set_auth_token(self, auth_token):
    self._auth_token = auth_token
    self._auth_dict = jwt.decode(self.auth_token, options={"verify_signature":False})

  def set_refresh_token(self, refresh_token):
    self._refresh_time = datetime.now() + timedelta(seconds=self.refresh_lifetime)
    self._refresh_token = refresh_token
    self._refresh_dict = jwt.decode(self.refresh_token, options={"verify_signature":False})

  @property
  def refresh_expiration(self):
    return datetime.fromtimestamp(self._refresh_dict.get('expiration_date')).strftime("%m/%d/%Y, %H:%M:%S")

  @property
  def auth_expiration(self):
    return datetime.fromtimestamp(self._auth_dict.get('expiration_date')).strftime("%m/%d/%Y, %H:%M:%S")

  @property
  def tokens_valid(self):
    try:
      r_exp = self._refresh_dict.get('expiration_date')
      a_exp = self._auth_dict.get('expiration_date')
      now = datetime.now().timestamp()
      return r_exp > now and a_exp > now
    except:
      return False

  def logout(self):
    self._auth_token = ""
    self._refresh_token = ""
    self.set_logged_in(False)

  def set_server(self, server):
    self._server = server

  def due(self) -> bool:
    if not self.logged_in:
      return False
    now = datetime.now()
    try:
      if now > self._refresh_time:
        return True
      else:
        return False
    except Exception as err:
      print("Error for user {}: {}".format(self.username, err))
      return False

  def refresh(self, forced=False):
    if self.due() or forced == True:
      self._server.refresh_user_token(self)

  @property
  def logged_in(self) -> bool:
    return self._logged_in

  def set_logged_in(self, state):
    self._logged_in = state

  @property
  def unqueue(self):
    return not self.logged_in

  def __eq__(self, __o: object) -> bool:
    try:
      if isinstance(__o, User):
        return (
          self._username == __o._username and
          self._password == __o._password
          )
      else:
        return False
    except:
      return False

  def __repr__(self) -> str:
    return f""" {self._username}: {self._password}, Logged in: {self._logged_in}"""