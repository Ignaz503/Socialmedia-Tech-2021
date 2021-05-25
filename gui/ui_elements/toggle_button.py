from enum import Enum
from multiprocessing.connection import wait
import threading
from tkinter import Button, NSEW
from tkinter.constants import END
from typing import Callable
from utility.waitableobject import Waitable_Object
from utility.simple_logging import Logger

class Toggle_Button(Button):
  __on_true: Callable
  __on_false: Callable
  __running_text:str
  __stopped_text:str
  __state: bool
  def __init__(self,
      on_true:Callable,
      on_false:Callable,when_true:str,
      when_false:str,
      *args,
      **kwargs):
    super().__init__(text=when_false, command= self.switch,relief="raised",*args,**kwargs)
    self.__state = False
    self.__running_text = when_true
    self.__stopped_text = when_false
    self.__on_true = on_true
    self.__on_false = on_false
    
  def get_state(self):
    return self.__state
  
  def switch(self):
    if self.__state:
      self._handle_state_switch_true_to_false()
    else:
      self._handle_state_switch_false_to_true()

  def _handle_state_switch_true_to_false(self):
    self.__state = False
    self.configure(text=self.__stopped_text,relief="raised")
    self.__on_false()

  def _handle_state_switch_false_to_true(self):
    self.__state = True
    self.configure(text=self.__running_text,relief="sunken")
    self.__on_true()
  
class WaitOptions(Enum):
  TRUE_TO_FALSE = 0
  FALSE_TO_TRUE = 1

class DelayedToggleButton(Toggle_Button):
  __wait_on: Waitable_Object
  __before_wait_action:Callable
  __wait_when: WaitOptions
  __wait_mesage: str
  __wait_event: threading.Event
  __logger: Logger
  def __init__(self,
      wait_when:WaitOptions,
      wait_on: Waitable_Object,
      before_wait_action:Callable,
      wait_message:str,
      logger:Logger,
      *args,
      **kwargs):
    super().__init__(*args, **kwargs)
    self.__wait_when = wait_when
    self.__wait_mesage = wait_message
    self.__wait_on = wait_on
    self.__before_wait_action = before_wait_action
    self.__wait_event = threading.Event()
    self.__logger = logger

  def change_wait_on_object(self, new_obj: Waitable_Object):
    self.__wait_on = new_obj

  def switch(self):
    if self.get_state():
      if self.__wait_when is WaitOptions.TRUE_TO_FALSE:
        self.__kick_off_wait_thread(lambda: self.__when_awaited(self._handle_state_switch_true_to_false))
      else:
        self._handle_state_switch_true_to_false()
    else:
      if self.__wait_when is WaitOptions.FALSE_TO_TRUE:
        self.__kick_off_wait_thread(lambda: self.__when_awaited(self._handle_state_switch_false_to_true))
      else:
        self._handle_state_switch_false_to_true()
  
  def __when_awaited(self,after: Callable):
    self.configure(state = 'normal')
    after()
    self.__wait_event.set()

  def __kick_off_wait_thread(self, when_awaited: Callable):
    self.configure(state='disabled',text=self.__wait_mesage)
    self.__wait_event.clear()
    self.__before_wait_action()
    thread = threading.Thread(name="wait thread", target=DelayedToggleButton.__wait,args=(self.__wait_on,when_awaited, self.__logger))
    thread.start()

  @staticmethod
  def __wait(obj: Waitable_Object,when_awaited: Callable,  logger:Logger):
    obj.wait()
    when_awaited()


