from inspect import signature

class InvokeArgumentCountMismatch(Exception):
  def __init__(self, *args: object) -> None:
      super().__init__("argument length on invoke does not match argument count when created",*args)

class NonCallableRegisterAttempt(Exception):
  def __init__(self, *args: object) -> None:
      super().__init__("Tried to register a non callable to an event",*args)

class RegisterFunctionArgumentCountMismatch(Exception):
  def __init__(self, *args: object) -> None:
      super().__init__("Tried to register a function with a incorrect amount of arguments",*args)

class EventRegisterUnknownArgumentName(Exception):
  def __init__(self,arg_name:str,*args: object) -> None:
      super().__init__(f"{arg_name} is an unknown argument name",*args)

class EventRegisterArgumentTypeMismatch(Exception):
  def __init__(self,arg_name,expected,got, *args: object) -> None:
      super().__init__(f"Argument {arg_name} type {got} does not match {expected}",*args)

class InvokeUnkownArgumentName(Exception):
  def __init__(self,arg_name:str, *args: object) -> None:
    super().__init__(f"{arg_name} is an uknown argument name",*args)

class InvokeArgumentTypeMismatch(Exception):
  def __init__(self,arg,got,expected, *args: object) -> None:
      super().__init__(f"Argument {arg} type {got} does not match {expected}",*args)

class Event:
  def __init__(self,strict_typing=False,**kwargs):
    self.__args = {}
    self.__strict_typing = strict_typing
    self.__args.update(kwargs)
    self.__registerd = []

  def invoke(self,**kwargs):
    if len(kwargs) != len(self.__args):
      raise InvokeArgumentCountMismatch()
    
    for k,value in kwargs.items():
      if k not in self.__args:
        raise InvokeUnkownArgumentName(k)
      if self.__strict_typing:
        if type(value) != self.__args[k]:
          raise InvokeArgumentTypeMismatch(k,type(value),self.__args[k])
    for func in self.__registerd:
      func(**kwargs)

  def register(self,to_register):
    if not callable(to_register):
      raise NonCallableRegisterAttempt()
    sig = signature(to_register)
    if len(sig.parameters) != len(self.__args):
      raise RegisterFunctionArgumentCountMismatch()

    for param_name in sig.parameters:
      if param_name not in self.__args:
        raise EventRegisterUnknownArgumentName(param_name)
      if self.__strict_typing:
        if self.__args[param_name] != sig.parameters[param_name].annotation:
          raise EventRegisterArgumentTypeMismatch(param_name,self.__args[param_name],sig.parameters[param_name].annotation)

    self.__registerd.append(to_register)

  def __call__(self, **kwds):
    self.invoke(**kwds)

  def __str__(self) -> str:
    s = "event:\n"
    s+= f"  strict typing: {self.__strict_typing}\n"
    s+= "  arguments: " + str(self.__args)+"\n"
    s+="  registerd:\n"
    for r in self.__registerd:
      s+="    - "+str(r.__name__)
    return s

  def unregister(self,to_unregister):
    try:
      self.__registerd.remove(to_unregister)
    except ValueError:
      pass