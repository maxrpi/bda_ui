import PySimpleGUI as sg
import pandas as pd
import dateutil.parser
import datetime
import bda_service
import refresher

from UI.page import Page
from bdaTrain.layout import layout
from bdaTrain.event_handler import event_handler
from bdaTrain.actions import actions
from bdaTrain.initializers import initializers
from bdaTrain.callbacks import callbacks

page = Page(
  name="BDAtrain",
  layout=layout,
  event_handler=event_handler
  initializers=initializers,
  actions = actions,
  callbacks=callbacks,
  )



known_attributes = {}
avail_keys = list(known_attributes.keys())
inputs_keys = []
outputs_keys = []
top_text_width=16
sorter_width = 30
bda_token_expiration = "no token"
smip_auth = {}
startTimeObj = None
endTimeObj = None
my_settings_copy = {}
user = None