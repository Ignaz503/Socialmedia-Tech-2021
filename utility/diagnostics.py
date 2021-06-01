import time
from typing import Any, Callable
from utility.simple_logging import Logger, Level
from utility.event import Event
from utility.math import get_hours_minutes_seconds_ms

class Data_Handler:
  def __init__(self) -> None:
    pass
  def update(self, current_value, new_value):
    return None
  def log(self, value, logger: Logger):
    pass
  def init_value(self):
    return None
  def to_string(self, value) -> str:
      return ""


class Diagnostics:
  __data: dict[str, Any]
  __data_handler: dict[str,Data_Handler]
  __update_event:Event

  def __init__(self) -> None:
      self.__data = {}
      self.__data_handler = {}
      self.__update_event = Event(category=str,value=str)
  
  def create_category(self, name: str, handler: Data_Handler):
    self.__data[name] = handler.init_value()
    self.__data_handler[name] = handler

  def update_value(self, category: str, data):
    if category in self.__data:
      old_val = self.__data[category]
      self.__data[category] = self.__data_handler[category].update(old_val,data)
      self.__update_event(category=category,value=self.__data_handler[category].to_string(self.__data[category]))
  
  def reset_value(self, category:str):
    self.update_value(category,self.__data_handler[category].init_value())

  def display_category(self, category: str, logger: Logger):
    if category in self.__data_handler:
      self.__data_handler[category].log(self.__data[category],logger)

  def get(self, category: str, as_string: bool = False):
    if category in self.__data:
      if as_string:
        return self.__data_handler[category].to_string(self.__data[category])
      return self.__data[category]
    return None

  def categories(self):
    for category in self.__data:
      yield category

  def register_to_update(self,to_register: Callable[[str,str],None]):
    self.__update_event.register(to_register)

  def log(self, logger: Logger):
    for key in self.__data:
      self.display_category(key,logger)

  def __stringify_category(self, category:str)->str:
    if category in self.__data_handler:
      return self.__data_handler[category].to_string(self.__data[category])
    return f"{category} has no data handler"

  def to_string(self)->str:
    return str(self)

  def __str__(self) -> str:
    s = ""
    for key in self.__data:
      s+=self.__stringify_category(key)+"\n"
    return s

  def reset(self):
    for key in self.__data:
      self.update_value(key,self.__data_handler[key].init_value())

class Increment_Data_Handler(Data_Handler):
    def __init__(self, start_value) -> None:
      self.start_value = start_value
    
    def update(self, current_value, new_value):
      return current_value + new_value
      
    def log(self, value, logger: Logger):
      logger.log(self.build_message(value),Level.INFO)
    
    def build_message(self, value):
      return str(value)

    def to_string(self, value) -> str:
        return self.build_message(value)

    def init_value(self):
      return self.start_value

class Counting_Data_Handler(Increment_Data_Handler):
  message_end: str
  def __init__(self, start_value = 0, message_end: str = "") -> None:
      super().__init__(start_value)
      self.message_end = message_end

  def log(self,value,logger: Logger):
    logger.log("A total of {val} ".format(val = value) + self.message_end)

class Timer_Data_Handler(Data_Handler):
    def __init__(self) -> None:
      pass   
    def update(self, current_value, new_value):
      if new_value is not None:
        current_value[1] = -1.0
      else:
        current_value[1] = time.perf_counter()
      return current_value
      
    def log(self, value, logger: Logger):
      logger.log(self.build_message(value),Level.INFO)
 
    def build_message(self, value):
      if value[1] < 0:
        return "--h:--m:--.----s"
      h,m,s = get_hours_minutes_seconds_ms(self.seconds_passed(value))
      return f"{h}h:{m}m{s:0.4f}s"

    def to_string(self, value) -> str:
        return self.build_message(value)

    def seconds_passed(self, value:list[float]):
      if len(value) < 2:
        return 0
      return value[-1]-value[0]

    def init_value(self):
      return [time.perf_counter(),-1.0]

class TextDataHandler(Data_Handler):
  __start_value:str
  def __init__(self, start_value:str) -> None:
    self.__start_value = start_value
  
  def update(self, current_value, new_value):
    return new_value
    
  def log(self, value, logger: Logger):
    logger.log(value, Level.INFO)
  
  def build_message(self, value):
    return value

  def to_string(self, value) -> str:
    return value

  def init_value(self):
    return self.__start_value