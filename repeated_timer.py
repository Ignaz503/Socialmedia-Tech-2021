#stackoverflow goodness + repetion max
import threading 

class Repeat_Timer(object):
  def __init__(self, interval, function, *args, **kwargs):
    self._timer     = None
    self.interval   = interval
    self.function   = function
    self.args       = args
    self.kwargs     = kwargs
    self.is_running = False

  def __run(self):
    self.is_running = False
    self.function(*self.args, **self.kwargs)
    self.start()

  def start(self):
    if not self.is_running:
        self._timer = threading.Timer(self.interval, self.__run)
        self._timer.start()
        self.is_running = True
  
  def start_running(self):
    #hacks
    self._timer = threading.Timer(0.1,self.__run)
    self.is_running = True
    self._timer.start()

  def stop(self):
    self._timer.cancel()
    self.is_running = False

