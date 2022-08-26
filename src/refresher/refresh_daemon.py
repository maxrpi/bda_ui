import threading
import time

class RefreshDaemon(object):
  def __init__(self, interval):
    self._th =  None
    self._interval = interval
    self._locked = False
    self.todo = set()

  def add_task(self, item):
    while self._locked:
      time.sleep(0.5)
    self._locked = True
    self.todo.add(item)
    self._locked = False

  def check_items(self):
    self._locked = True
    for item in self.todo:
      item.refresh()
    self._locked = False

  def run(self):
    self._th = threading.Thread(target=self.loop, daemon=True)
    self._th.start()

  def loop(self):
    self.running = True
    while self.running == True:
      self.check_items()
      time.sleep(self._interval)
  
  def stop(self):
    self.running = True
    self._th.join()