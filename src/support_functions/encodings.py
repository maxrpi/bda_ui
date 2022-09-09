import numpy as np
import pickle
from base64 import urlsafe_b64decode, urlsafe_b64encode
from typing import Union

def encode_base64(data : Union[bytes, str]) -> str:
  if isinstance(data, str):
    return urlsafe_b64encode(data.encode("utf-8")).decode('ascii')
  else:
    return urlsafe_b64encode(data).decode('ascii')

def decode_base64(b64_str : str) -> bytes:
  return urlsafe_b64decode(b64_str)

# return pickled version of datatype
def b64encode_datatype(data) -> str:
  return urlsafe_b64encode(
    pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
  ).decode('ascii')

# return unpickled version of string
def b64decode_datatype(string: str):
  return  pickle.loads(urlsafe_b64decode(string))
