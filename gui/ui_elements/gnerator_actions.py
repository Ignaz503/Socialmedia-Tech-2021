from math import exp
from textwrap import fill

from numpy import right_shift
from utility.data_util import DataLocation
import utility.data_util as data_util
import os
import platform
import subprocess
from defines import VIS_ARGS
from tkinter.constants import BOTTOM, LEFT, RIGHT, TOP, TRUE
from utility.simple_logging import Level
from tkinter import Button, Frame, NS,X
from gui.ui_elements.ui_element import UIElement
from gui.ui_elements.toggle_button import DelayedToggleButton

from utility.cancel_token import Cancel_Token
from gui.ui_elements.toggle_button import WaitOptions

import generators.data_generator as data_generator
import generators.visualization_generator as visualization_generator

class GeneratorActions(UIElement):
  __data_generation_btn: DelayedToggleButton
  __visualization_generation_button: DelayedToggleButton

  __data_generation_cancel_token: Cancel_Token
  __visualization_cancel_token: Cancel_Token
  __show_btn_frame:Frame
  __created_vis:bool

  def __init__(self,*args,**kwargs) -> None:
    self.__data_generation_btn = None
    self.__visualization_generation_button = None
    self.__show_btn_frame= None
    self.__created_vis=False
    self.__data_generation_cancel_token = Cancel_Token()
    self.__visualization_cancel_token = Cancel_Token()
    super().__init__(*args,**kwargs)
  
  def _build(self) -> None :

    generator_button_frame = Frame(master=self)
    generator_button_frame.pack(side=TOP,fill=X,padx=5,pady=5, expand=True)

    self.__data_generation_btn =DelayedToggleButton(
      wait_when=WaitOptions.TRUE_TO_FALSE,
      wait_on= self.__data_generation_cancel_token,
      before_wait_action= lambda: self.__data_generation_cancel_token.request_cancel(),
      wait_message="waiting on data processing to stop",
      logger=self.application.get_logger(),
      on_true= self.__run_data_generation,
      on_false= lambda: None,
      when_true="stop data processing",
      when_false="start data processing",
      master=generator_button_frame)  
    self.__data_generation_btn.pack(side=LEFT,fill=X, padx=5, expand=TRUE)

    self.__visualization_generation_button = DelayedToggleButton(
      wait_when=WaitOptions.TRUE_TO_FALSE,
      wait_on= self.__visualization_cancel_token,
      before_wait_action = lambda: self.__visualization_cancel_token.request_cancel(),
      wait_message="waiting on data visualization",
      logger= self.application.get_logger(),
      on_true= self.__run_stream_observation,
      on_false=lambda: None,
      when_true="stop data visualization",
      when_false="start data viusalization",
      master=generator_button_frame)   
    self.__visualization_generation_button.pack(side=RIGHT,fill=X, padx=5,expand=TRUE)

    self.__show_btn_frame = Frame(master=self)
    self.__pack_show_btn_frame()

    if not self.__created_vis:
      self.__show_btn_frame.pack_forget()
 
    btn = Button(master=self.__show_btn_frame,
        text="Show Subreddit Subreddit Graph",
        command=self.__show_subreddit_subreddit_vis)
    btn.pack(side=LEFT,fill=X,padx=5,expand=True)

    btn = Button(master=self.__show_btn_frame,
        text="Show Subreddit User Graph",
        command=self.__show_subreddit_user_vis)
    btn.pack(side=RIGHT,fill=X,padx=5,expand=True)

  def __pack_show_btn_frame(self):
    self.__show_btn_frame.pack(side=BOTTOM,fill=X,pady=5,padx=5,expand=True)


  def __run_data_generation(self):
    self.__data_generation_cancel_token = Cancel_Token()
    self.__data_generation_btn.change_wait_on_object(self.__data_generation_cancel_token)
    data_generator.run(
      config= self.application.config,
      logger=self.application.get_logger(),
      token=self.__data_generation_cancel_token,
      on_done_callback=lambda: self.__data_generation_btn.switch())

  def __run_stream_observation(self):
    self.__visualization_cancel_token = Cancel_Token()
    self.__visualization_generation_button.change_wait_on_object(self.__visualization_cancel_token)
    visualization_generator.run(
      config = self.application.config,
      logger= self.application.get_logger(),
      token = self.__visualization_cancel_token,
      on_done_callback= self.__visualization_callback )

  def __visualization_callback(self):
    self.__visualization_generation_button.switch()
    if not self.__created_vis:
      self.__created_vis = True
      self.__pack_show_btn_frame()

  def any_action_running(self)->bool:
    return self.__data_generation_btn.get_state() or self.__visualization_generation_button.get_state()

  def __show_subreddit_subreddit_vis(self):
    self.__show_visualization(visualization_generator.SUBREDDIT_SUBREDDIT_VISUALIZATION_NAME)

  def __show_subreddit_user_vis(self):
    self.__show_visualization(visualization_generator.SUBREDDIT_USER_VISUALIZATION_NAME)

  def __show_visualization(self, file: str):
    filepath = data_util.make_data_path(file,  DataLocation.VISUALIZATION)
    filepath = os.path.join(os.getcwd(),filepath)

    if platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', filepath))
    elif platform.system() == 'Windows':    # Windows
        os.startfile(filepath)
    else:                                   # linux variants
        subprocess.call(('xdg-open', filepath))