from math import exp
from tkinter import LEFT, Label
from tkinter.constants import X
from utility.app_config import Config
from gui.ui_elements.ui_element import UIElement
from gui.ui_elements.input_box import Time_H_M_S_InputBox 
from defines import MIN_BATCH_SAVE_TIME
from utility.math import get_hours_minutes_seconds,get_seconds

class StreamSettings(UIElement):

  __input_box: Time_H_M_S_InputBox
  def __init__(self, *args, **kwargs) -> None:
    self.__input_box = None
    super().__init__( *args, **kwargs)
  
  def _build(self):
    c: Config = self.application.config
    t = c.stream_save_interval_seconds
    if t <  MIN_BATCH_SAVE_TIME:
      t = MIN_BATCH_SAVE_TIME

    hms = get_hours_minutes_seconds(t)

    self.__input_box = Time_H_M_S_InputBox(title="Save gathered data every:",
        on_update=self.__on_time_input_update,
        init_vals = hms,
        application=self.application,
        master=self)
    self.__input_box.pack(side=LEFT,expand=True,fill=X,padx=5)
 
  def __on_time_input_update(self,hms):
    seconds = get_seconds(hms)
    if seconds < MIN_BATCH_SAVE_TIME:
      time = get_hours_minutes_seconds(MIN_BATCH_SAVE_TIME)
      self.__input_box.set_hours_min_seconds(time)
    else:
      self.application.set_config_value("stream_save_interval_seconds",seconds)



