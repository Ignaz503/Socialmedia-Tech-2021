import threading
from enum import Enum
from typing import Callable
from utility.waitableobject import Waitable_Object

class UnauhthorizedAcknowledgeAttempt(Exception):
  allowed_indent: int
  raised_indent: int
  def __init__(self,allwoed_indent: int, raised_indent:int, *args: object) -> None:
      self.allowed_indent = allwoed_indent
      self.raised_indent = raised_indent
      message = "Unauhtorized thread (id: {r}) tried to inform of cancelation finish. Only thread with id: {i} is allowed to".format(r=raised_indent,i=allwoed_indent)
      super().__init__(message, *args)

class TokenTrayUnsetAttempt(Exception):
  def __init__(self, *args: object) -> None:
      super().__init__("An attempt was made to unset the token of an already set token tray", *args)

class TokenTrayTokenChangeAttempt(Exception):
  def __init__(self, *args: object) -> None:
      super().__init__("An attempt was made to cahnge the token of an already set token tray", *args)

class Cancel_Token(Waitable_Object):
  __cancel_request: bool
  __cancel_event: threading.Event
  __listener_lock: threading.Lock
  __listeners: dict[int,bool]
  def __init__(self) -> None:
      self.__cancel_request = False
      self.__cancel_event = threading.Event()
      self.__listener_lock = threading.Lock()
      self.__listeners = {}

  def request_cancel(self):
    self.__cancel_request = True

  def is_cancel_requested(self):
    return self.__cancel_request
  
  def __acknowledge_token(self):
    with self.__listener_lock:
      self.__listeners[threading.get_ident()] = False

  def __inform_finsihed_cancel(self):
    with self.__listener_lock:
      self.__listeners[threading.get_ident()] = True
      values = self.__listeners.values()
    if all(value == True for value in values):
      self.__cancel_event.set()

  def wait(self):
    with self.__listener_lock:
      if len(self.__listeners) == 0:
        return #don't wait on event if noone acknowledged the token
    self.__cancel_event.wait()

  def __enter__(self):
    self.__acknowledge_token()
    return self
  def __exit__(self, type, value, traceback):
      if traceback is not None:
        print(traceback)
      self.__inform_finsihed_cancel()


class Thread_Owned_Cancel_Token(Waitable_Object):
  __cancel_request: bool
  __owner_id: int
  __cancel_event: threading.Event
  def __init__(self) -> None:
      self.__cancel_request = False
      self.__owner_id = threading.get_ident()
      self.__cancel_event = threading.Event()

  def request_cancel(self):
    self.__cancel_request = True
  
  def is_cancel_requested(self):
    return self.__cancel_request

  def __inform_finsihed_cancel(self):
    if threading.get_ident() != self.__owner_id:
      raise UnauhthorizedAcknowledgeAttempt(self.__owner_id,threading.get_ident())
    self.__cancel_event.set()

  def wait(self):
    self.__cancel_event.wait()

  def request_cancel_and_wait(self):
    self.request_cancel()
    self.wait()

  def __enter__(self):
      return self
  def __exit__(self, type, value, traceback):
      if traceback is not None:
        print(traceback)
      self.__inform_finsihed_cancel()

class TrayOperationStatus(Enum):
  SUCCESS = 0
  NO_TOKEN = 0

class Thread_Owned_Token_Tray(Waitable_Object):
  __token: Thread_Owned_Cancel_Token
  __token_lock = threading.Lock
  def __init__(self) -> None:
      self.__token = None
      self.__token_lock = threading.Lock()
  
  def set_token(self, token: Thread_Owned_Cancel_Token):
    if self.has_token():
      if token is None:
        raise TokenTrayUnsetAttempt()
      else:
        raise TokenTrayTokenChangeAttempt()   
    with self.__token_lock:
      self.__token = token
  
  def has_token(self):
    with self.__token_lock:
      return self.__token is not None
  
  def __get_token(self) -> Thread_Owned_Cancel_Token:
    with self.__token_lock:
      return self.__token

  def __try_token_operation(self,operation: Callable[[Thread_Owned_Cancel_Token],TrayOperationStatus])-> TrayOperationStatus:
    if not self.has_token():
      return TrayOperationStatus.NO_TOKEN
    return operation(self.__get_token())

  def __wait_operation(self, tk: Thread_Owned_Cancel_Token)-> TrayOperationStatus:
    tk.wait()
    return TrayOperationStatus.SUCCESS

  def try_wait(self) -> TrayOperationStatus:
    return self.__try_token_operation(self.__wait_operation)

  def wait(self):
    self.try_wait()

  def __request_cancel_operation(self, tk: Thread_Owned_Cancel_Token):
    tk.request_cancel()
    return TrayOperationStatus.SUCCESS

  def try_rqeuest_cancel(self):
    return self.__try_token_operation(self.__request_cancel_operation)

  def try_request_cancel_and_wait(self)-> TrayOperationStatus:
    status = self.try_rqeuest_cancel()
    if status is TrayOperationStatus.SUCCESS:
      status = self.try_wait()
    return status

  