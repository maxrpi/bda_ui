import threading
import time

class Element(object):
  def __init__(self):
    pass

  def set_refresh_function(self, refresh_function):
    self._refresh_function = refresh_function
  
  def refresh(self):
    self._refresh_function()

  @property
  def unqueue(self):
    return False

class RefreshDaemon(object):
  def __init__(self) -> None:
    self._initialized = False

  def initialize(self, interval):
    self._th = threading.Thread(target=self.loop, daemon=True)
    self._interval = interval
    self._locked = False
    self.todo = set()
    self._paused = False
    self._initialized = True

  def add_task(self, item):
    while self._locked:
      time.sleep(0.5)
    self._locked = True
    self.todo.add(item)
    self._locked = False

  def check_items(self):
    self._locked = True
    for item in list(self.todo):
      try:
        if item.unqueue:
          self.todo.remove(item)
        item.refresh()
      except Exception as err:
        print(err)
    self._locked = False

  def run(self):
    self._th.start()
    self._running = True
    self._paused = False

  def loop(self):
    self.running = True
    while self.running == True:
      if not self._paused:
        self.check_items()
      time.sleep(self._interval)
  
  def pause(self):
    self._paused = True

  def unpause(self):
    self._paused = False

  def stop(self):
    self.running = False
    self._th.join()