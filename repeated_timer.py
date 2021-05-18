#stackoverflow goodness + repetion max
import threading 
import time

class RepeatedTimer(object):
  def __init__(self, interval, max_num_rep, function, *args, **kwargs):
    self._timer     = None
    self.interval   = interval
    self.function   = function
    self.args       = args
    self.kwargs     = kwargs
    self.is_running = False
    self.max_num_rep = max_num_rep
    self.rep = 0

  def _run(self):
    self.is_running = False
    self.rep +=1
    self.function(*self.args, **self.kwargs)
    self.start()

  def start(self):
    if not self.is_running and self.rep < self.max_num_rep:
        self._timer = threading.Timer(self.interval, self._run)
        self._timer.start()
        self.is_running = True
    elif self.rep >= self.max_num_rep:
      self.stop()

  def stop(self):
    self._timer.cancel()
    self.is_running = False