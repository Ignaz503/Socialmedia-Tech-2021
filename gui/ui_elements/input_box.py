from tkinter import Entry,Event,Misc, Frame, Label, LEFT,X, StringVar
from typing import Callable
from gui.ui_elements.ui_element import UIElement
import math

class EnterAcceptInputBox(Entry):
  __on_accept: Callable
  __focus_target: Misc
  def __init__(self,on_accept: Callable[[Event],None],focus_target:Misc=None, *args, **kwargs) -> None:
    super().__init__(*args,**kwargs)
    self.bind('<Return>',lambda event: self.__on_key_enter(event))
    self.__on_accept = on_accept
    if focus_target == None:
      self.__focus_target = self.master
    else:
      self.__focus_target = focus_target

  def __on_key_enter(self,event: Event):
    self.__focus_target.focus_set()
    self.__on_accept(event)

class Time_H_M_S_InputBox(UIElement):

  __var_hours: StringVar
  __var_minutes: StringVar
  __var_seconds: StringVar
  __title: str
  __prev_hours:int
  __prev_minutes:int
  __prev_seconds:int
  __on_upate: Callable[[tuple[int,int,int]],None]
  def __init__(self,
      title:str,
      on_update: Callable[[tuple[int,int,int]],None],
      init_vals: tuple[int,int,int] = (0,0,0),
      *args,
      **kwargs) -> None:

    self.__var_hours = StringVar()
    self.__var_hours.set(init_vals[0])
    self.__prev_hours = init_vals[0]

    self.__var_minutes = StringVar()
    self.__var_minutes.set(init_vals[1])
    self.__prev_minutes = init_vals[1]

    self.__var_seconds = StringVar()
    self.__var_seconds.set(init_vals[2])
    self.__prev_seconds = init_vals[2]

    self.__title = title
    self.__on_upate = on_update

    super().__init__(*args, **kwargs)

  def _build(self):
    l = Label(master=self,text=self.__title)
    l.pack(side=LEFT,expand=True,fill=X, padx=5)

    input_box_frame = Frame(master= self)
    input_box_frame.pack(expand=True, fill=X, pady=5)

    l = Label(master=input_box_frame,text="H:")
    l.pack(side=LEFT,expand=True,fill=X, padx=5)

    input_box = EnterAcceptInputBox(on_accept=lambda e: self.__parse_hours(),
      focus_target=self.master,
      master=input_box_frame,
      textvariable=self.__var_hours)
    input_box.configure(
      validate="focusout",
      validatecommand= self.__parse_hours)
    input_box.pack(side=LEFT,fill=X,padx=5,expand=True)
    input_box.bind("<FocusIn>",lambda e: self.__store_current_val_hours())

    l = Label(master=input_box_frame,text="M:")
    l.pack(side=LEFT,expand=True,fill=X, padx=5)

    input_box = EnterAcceptInputBox(on_accept=lambda e: self.__parse_minutes(self.__var_minutes.get()),
      focus_target=self.master,
      master=input_box_frame,
      textvariable=self.__var_minutes)
    input_box.configure(
      validate="focusout",
      validatecommand= self.__minutes_validate_wrapper)
    input_box.pack(side=LEFT,fill=X,padx=5,expand=True)
    input_box.bind("<FocusIn>",lambda e: self.__store_current_val_minutes())

    l = Label(master=input_box_frame,text="S:")
    l.pack(side=LEFT,expand=True,fill=X, padx=5)
    input_box = EnterAcceptInputBox(on_accept=lambda e: self.__parse_seconds(),
      focus_target=self.master,
      master=input_box_frame,
      textvariable=self.__var_seconds)
    input_box.configure(
      validate="focusout",
      validatecommand= self.__parse_seconds)
    input_box.pack(side=LEFT,fill=X,padx=5,expand=True)
    input_box.bind("<FocusIn>",lambda e: self.__store_current_val_seconds())

  def __minutes_validate_wrapper(self):
    self.__parse_minutes(self.__var_minutes.get())

  def __store_current_val_hours(self):
    self.__prev_hours = int(self.__var_hours.get())

  def __store_current_val_minutes(self):
    self.__prev_minutes = int(self.__var_minutes.get())

  def __store_current_val_seconds(self):
    self.__prev_seconds = int(self.__var_seconds.get())

  def __parse_hours(self):
    try:
      val = int(self.__var_hours.get())
      self.__invoke_update()
    except ValueError:
      self.__var_hours.set(self.__prev_hours)

  def __parse_minutes(self,string: str):
    try:
      val = int(string)
      self.__handle_minute_propagation(val)
      self.__invoke_update()
    except ValueError:
      self.__var_minutes.set(self.__prev_minutes)

  def __handle_minute_propagation(self, val: float):
    if val / 60 >= 1.0:
      h_f = val / 60
      frac,full = math.modf(h_f)
      c = int(self.__var_hours.get())
      c += math.floor(full)
      self.__var_hours.set(c)
      self.__var_minutes.set(math.ceil(60*frac))
    else:
      self.__var_minutes.set(math.floor(val))

  def __handle_seconds_propagation(self,val:float):
    if val / 60 >= 1.0:
      m_f = val / 60
      m = math.floor(m_f)
      self.__parse_minutes(str(m))
      frac,full = math.modf(m_f)
      self.__var_seconds.set(str(math.ceil(60*frac)))
    else:
      self.__var_seconds.set(math.floor(val))

  def __parse_seconds(self):
    try:
      val = int(self.__var_seconds.get())
      self.__handle_seconds_propagation(val)
      self.__invoke_update()
    except ValueError:
      self.__var_seconds.set(self.__prev_seconds)

  def __get_hours_minutes_seconds(self)->tuple[int,int,int]:
    return (
      int(self.__var_hours.get()),
      int(self.__var_minutes.get()),
      int(self.__var_seconds.get())
    )
  
  def set_hours_min_seconds(self,hms:tuple[int,int,int]):
    self.__var_hours.set(hms[0])
    self.__var_minutes.set(hms[1])
    self.__var_seconds.set(hms[0])

  def __invoke_update(self):
    self.__on_upate(self.__get_hours_minutes_seconds())