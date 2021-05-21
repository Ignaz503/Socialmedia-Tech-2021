
class Logger:
  active: bool

  def __init__(self, active: bool) -> None:
      self.active = active
  
  def log(self, message: str):
    if self.active:
      print(message)
  
