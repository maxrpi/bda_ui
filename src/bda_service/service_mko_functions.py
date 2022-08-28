def register_mko(self, mko):
  url = self.baseurl + "/Train/create_MKO"
  data = mko.user.params
  data['model_name'] = mko.model_name
  response = requests.post(url, headers=mko.user.headers, data=data)
  claim_check = json.loads(response.content)['claim_check']
  return claim_check

def attach_data_to_mko(self, mko):
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