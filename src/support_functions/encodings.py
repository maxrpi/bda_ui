import numpy as np
import pickle
from base64 import b64decode, b64encode
import re

def encode_base64(some_bytes):
  return b64encode(some_bytes).decode('ascii')

def decode_base64(data, altchars=b'+/'):
  data = re.sub(rb'[^a-zA-Z0-9%s]+' % altchars, b'', data)  # normalize
  missing_padding = len(data) % 4
  if missing_padding:
    data += b'='* (4 - missing_padding)
  return b64decode(data, altchars)

# return unpickled version of string
def b64decode_array(string: str) -> np.ndarray:
  return  pickle.loads(b64decode(string))


# return pickled version of array
def b64encode_array(array: np.ndarray) -> str:
  return b64encode(
    pickle.dumps(array, protocol=pickle.HIGHEST_PROTOCOL)
  ).decode('ascii')