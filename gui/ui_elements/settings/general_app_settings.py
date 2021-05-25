from posixpath import expanduser
from tkinter import BooleanVar, Button, Checkbutton, Entry, Event, Frame, LEFT, Label, Misc, Radiobutton, StringVar
from tkinter.constants import BOTTOM, RIGHT, TOP, X
from tkinter.ttk import LabeledScale
from typing import Callable
from utility.simple_logging import Level, Logger
from utility.app_config import Config
from gui.ui_elements.ui_element import UIElement
from gui.ui_elements.reddit_secrets import Reddit_Crawl_Secrets
from defines import MIN_BATCH_SAVE_TIME
from gui.ui_elements.input_box import Time_H_M_S_InputBox
from utility.math import get_hours_minutes_seconds,get_seconds

class GeneralSettings(UIElement):
  __verbose: BooleanVar
  __time_input: Time_H_M_S_InputBox
  def __init__(self, *args, **kwargs) -> None:
      self.__verbose = BooleanVar()
      self.__verbose.set(False)
      self.__time_input = None
      super().__init__( *args, **kwargs)
      
  
  def _build(self):
    c: Config = self.application.config

    self.__verbose.set(c.verbose)
    r = Checkbutton(master = self,
       text="verbose",
       variable=self.__verbose,
       onvalue=True,
       offvalue=False,
       command=lambda: self.__update_verbose(),
       relief="groove",
       borderwidth=1)
    r.pack(side=TOP, padx=5, fill=X, expand=True)

    t = c.batch_save_interval_seconds
    if t < MIN_BATCH_SAVE_TIME:
      t = MIN_BATCH_SAVE_TIME
    hms = get_hours_minutes_seconds(t)

    self.__time_input = Time_H_M_S_InputBox(title="Save to disk interval:",
        on_update=self.__on_time_input_update,
        init_vals = hms,
        application=self.application,
        master=self,relief="groove",borderwidth=1)
    self.__time_input.pack(fill=X,padx=5, pady=5,expand=True)

    btn = Button(master = self, text="Log current configuration", command=self.__log_config)
    btn.pack(side=BOTTOM,fill=X,expand=True,pady=5,padx=5)
  def __log_config(self):
    self.application.log(str(self.application.config))

  def __update_verbose(self):
    #haky focus change for entry
    self.master.focus_set()
    self.application.set_config_value('verbose',self.__verbose.get())
    l: Logger = self.application.get_logger()
    l.set_active(self.__verbose.get())

  def __on_time_input_update(self,hms:tuple[int,int,int]):
    seconds = get_seconds(hms)
    if seconds < MIN_BATCH_SAVE_TIME:
      time = get_hours_minutes_seconds(MIN_BATCH_SAVE_TIME)
      self.__time_input.set_hours_min_seconds(time)
    else:
      self.application.set_config_value("batch_save_interval_seconds",seconds)


