
class Page(object):
  def __init__(
    self,
    name=None,
    layout=None,
    event_handler=None,
    initializers=None,
    actions=None,
    settings=None,
    callbacks=None,
    ):
    if name is not None: self._name = name
    if layout is not None: self._layout = layout
    if event_handler is not None: self._event_handler = event_handler
    if initializers is not None: self._initializers = initializers
    if actions is not None: self._actions = actions
    if settings is not None: self.set_settings(settings)
    if callbacks is not None: self._callbacks = callbacks
  
  def set_initializers(self, initializers):
    self._initializers = initializers
  
  def initialize(self, window):
    for function in self._initializers:
      function(self, window)

  def set_layout(self, layout: list):
    self._layout = layout
  
  @property
  def layout(self):
    return self._layout
  
  def set_actions(self, actions):
    self._actions = actions

  def set_event_handler(self, event_handler):
    self._event_handler = event_handler

  @property
  def event_handler(self):
    return self._event_handler

  def set_settings(self, settings):
    self._settings = settings[self.name]
  
  def set_callbacks(self, callbacks):
    self._callbacks = callbacks
  
  def callback(self, name, *args, **kwargs):
    return self._callbacks[name](self, *args, **kwargs)
  
  @property
  def settings(self):
    return self._settings

