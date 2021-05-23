import time
from typing import Any
from utility.simple_logging import Logger, Level

class Data_Handler:
  def __init__(self) -> None:
    pass
  def update(self, current_value, new_value):
    return None
  def log(self, value, logger: Logger):
    pass
  def init_value(self):
    return None


class Diagnostics:
  data: dict[str, Any]
  data_handler: dict[str,Data_Handler]

  def __init__(self) -> None:
      self.data = {}
      self.data_handler = {}
  
  def create_category(self, name: str, handler: Data_Handler):
    self.data[name] = handler.init_value()
    self.data_handler[name] = handler

  def update_value(self, category: str, data):
    if category in self.data:
      old_val = self.data[category]
      self.data[category] = self.data_handler[category].update(old_val,data)
  
  def display_category(self, category: str, logger: Logger):
    if category in self.data:
      self.data_handler[category].log(self.data[category],logger)

  def get(self, category: str):
    if category in self.data:
      return self.data[category]
    return None

  def log(self, logger: Logger):
    for key in self.data:
      self.display_category(key,logger)

  def reset(self):
    for key in self.data:
      self.data[key] = self.data_handler[key].init_value()

class Increment_Data_Handler(Data_Handler):
    def __init__(self, start_value) -> None:
      self.start_value = start_value
    
    def update(self, current_value, new_value):
      return current_value + new_value
      
    def log(self, value, logger: Logger):
      logger.log(self.build_message(value),Level.INFO)
    
    def build_message(self, value):
      return value

    def init_value(self):
      return self.start_value

class Total_Of_Incremnt_Data_Handler(Increment_Data_Handler):
  message_end: str
  def __init__(self, start_value = 0, message_end: str = "") -> None:
      super().__init__(start_value)
      self.message_end = message_end
  def build_message(self, value):
    return "A total of {val} ".format(val = value) + self.message_end

class Timer_Data_Handler(Data_Handler):
    def __init__(self) -> None:
      pass   
    def update(self, current_value, new_value):
      current_value.append(time.perf_counter())
      return current_value
      
    def log(self, value, logger: Logger):
      logger.log(self.build_message(value),Level.INFO)

    
    def build_message(self, value):
      return "{t:0.4f} seconds passed ".format(t = self.seconds_passed(value))

    def seconds_passed(self, value:list[float]):
      return value[-1]-value[0]

    def init_value(self):
      return [time.perf_counter()]

