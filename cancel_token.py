import threading

class UnauhthorizedAcknowledgeAttempt(Exception):
  allowed_indent: int
  raised_indent: int
  def __init__(self,allwoed_indent: int, raised_indent:int, *args: object) -> None:
      self.allowed_indent = allwoed_indent
      self.raised_indent = raised_indent
      message = "Unauhtorized thread (id: {r}) tried to inform of cancelation finish. Only thread with id: {i} is allowed to".format(r=raised_indent,i=allwoed_indent)
      super().__init__(message, *args)

class AttemptedOwnershiptheft(Exception):
  owner_indent: int
  thief_indent: int
  def __init__(self,owner_indent: int, thief_indent:int, *args: object) -> None:
      self.owner_indent = owner_indent
      self.thief_indent = thief_indent
      message = "Attempted ownership theft from thread (id: {t}). Owner is thread with id {i}".format(t=thief_indent,i = owner_indent)
      super().__init__(message, *args)

class Cancel_Token:
  __cancel_request: bool
  __owner_id: int
  __cancel_event: threading.Event
  __onwership_taken:bool
  def __init__(self) -> None:
      self.__cancel_request = False
      self.__onwership_taken = False
      self.__cancel_event = threading.Event()

  def take_ownership(self, new_owner_id: int):
    if self.__onwership_taken:
      raise AttemptedOwnershiptheft(self.__owner_id,new_owner_id)
    self.__onwership_taken = True
    self.__owner_id = new_owner_id

  def request_cancel(self):
    self.__cancel_request = True
  
  def is_cancel_requested(self):
    return self.__cancel_request 

  def inform_finsihed_cancel(self):
    if threading.get_ident() != self.__owner_id:
      raise UnauhthorizedAcknowledgeAttempt(self.__owner_id,threading.get_ident())
    self.__cancel_event.set()

  def wait(self):
    self.__cancel_event.wait()

  def request_cancel_and_wait(self):
    self.request_cancel()
    self.wait()

  def has_finsiehd_cancel(self):
    return self.__cancel_event.is_set()
