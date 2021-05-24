from tkinter import Event, Frame, LEFT, Label, OptionMenu, StringVar
from tkinter.constants import BOTTOM, TOP, X
from typing import Callable
from utility.app_config import Config
from gui.ui_elements.ui_element import UIElement
from gui.ui_elements.input_box import EnterAcceptInputBox, Time_H_M_S_InputBox
from defines import GETTER_CATEGORY, GETTER_TYPE, MIN_REPEAT_TIME
from reddit_crawl.util.submission_getters import SubmissionGetters,TopCategories
import math
import utility.math as uma

class ActiveCrawlSettings(UIElement):

  __number_of_posts_var: StringVar
  __submission_getter_var: StringVar
  __category_var: StringVar
  __category_frame: Frame
  __time_input: Time_H_M_S_InputBox
  def __init__(self, *args, **kwargs) -> None:
    self.__number_of_posts_var = StringVar()
    self.__submission_getter_var = StringVar()
    self.__category_var = StringVar()
    self.__category_frame = None
    self.__time_input = None
    super().__init__(*args, **kwargs)
  
  def _build(self):

    frame = Frame(master = self,relief="groove",borderwidth=1)
    frame.pack(side=TOP, expand=True, fill=X,pady=5)

    l = Label(master=frame,text="Number of posts")
    l.pack(side=LEFT,expand=True)

    c: Config = self.application.config
    self.__number_of_posts_var.set(str(c.number_of_posts))
    input_box = EnterAcceptInputBox(on_accept=self.__on_accept,
          focus_target=self.master,
          master=frame,
          textvariable=self.__number_of_posts_var)
    input_box.configure(
      validate="focusout",
      validatecommand= self.__parse_number_of_posts)
    input_box.pack(fill=X,padx=5,expand=True)

    submissiton_getter_master_frame = Frame(master = self,
    relief="groove",borderwidth=1)
    submissiton_getter_master_frame.pack(expand=True, fill=X, pady=5)

    submissiton_getter_frame = Frame(master = submissiton_getter_master_frame,
      relief="groove",
      borderwidth=1)
    submissiton_getter_frame.pack(expand=True, fill=X, pady=5)

    l = Label(master=submissiton_getter_frame,text="Submissions to crawl:")
    l.pack(side=LEFT,expand=True, padx=5)

    self.__submission_getter_var.set(c.submission_getter[GETTER_TYPE])

    options = OptionMenu(submissiton_getter_frame,
      self.__submission_getter_var,
      *[e.value for e in SubmissionGetters],
      command=self.__handle_submission_getter_change)
    options.pack(side=TOP,fill=X,padx=5, expand=True)

    self.__category_frame = Frame(master = submissiton_getter_master_frame,
      relief="groove",
      borderwidth=1)
    self.__category_frame.pack(expand=True, fill=X, pady=5)
    
    l = Label(master=self.__category_frame,text="Category:")
    l.pack(side=LEFT,expand=True, padx=5)
    
    self.__try_set_category_var(c)
    category_drop_down = OptionMenu(self.__category_frame,
      self.__category_var,
      *[e.value for e in TopCategories],
      command=self.__handle_category_change)
    category_drop_down.pack(side=BOTTOM,fill=X,padx=5, expand=True)

    if c.submission_getter[GETTER_TYPE] != SubmissionGetters.TOP.value:
        self.__category_frame.pack_forget()

    t = (c.repeat_hours,c.repeat_minutes,c.repeat_seconds)
    if uma.get_seconds(t) < MIN_REPEAT_TIME:
      t = uma.get_hours_minutes_seconds(MIN_REPEAT_TIME)
      self.application.set_config_value("repeat_hours",t[0])
      self.application.set_config_value("repeat_minutes",t[1])
      self.application.set_config_value("repeat_seconds",t[2])

    self.__time_input = Time_H_M_S_InputBox(title="Repeat Every:",
        on_update=self.__on_time_input_update,
        init_vals = t,
        application=self.application,
        master=self,
        relief="groove",
        borderwidth=1)
    self.__time_input.pack(side= BOTTOM,expand=True, fill=X, pady=5)

  def __on_time_input_update(self,hms:tuple[int,int,int]):   
    seconds = uma.get_seconds(hms)
    #h,m,s = 
    #current_repeat_time = self.application.config.get_repeat_time_in_seconds()
    if seconds < MIN_REPEAT_TIME:
      time = uma.get_hours_minutes_seconds(MIN_REPEAT_TIME)
      self.__time_input.set_hours_min_seconds(time)
    else:
      h,m,s = hms
      self.application.set_config_value("repeat_hours",h)
      self.application.set_config_value("repeat_minutes",m)
      self.application.set_config_value("repeat_seconds",s)

    
  def __pack_category_frame(self):
    self.__category_frame.pack(expand=True, fill=X, pady=5)

  def __on_accept(self,e: Event):
    self.__parse_number_of_posts()

  def __parse_number_of_posts(self):
    try:
      string = self.__number_of_posts_var.get()
      
      if string == "None" or string == "none":
        self.application.set_config_value('number_of_posts',None)

      val = int(string)

      if val < 0:
        val = None

      if string == "None" or string == "none":
        self.application.set_config_value('number_of_posts',None)
    except ValueError:
      self.__number_of_posts_var.set(str(self.application.config.number_of_posts))
      pass
  
  def __try_set_category_var(self,c:Config):
    if GETTER_CATEGORY in c.submission_getter:
      self.__category_var.set(c.submission_getter[GETTER_CATEGORY])
    else:
      self.__category_var.set(TopCategories.ALL.value)

  def __handle_submission_getter_change(self,var: str):
    c:Config = self.application.config
    
    old_val = c.submission_getter[GETTER_TYPE]

    c.submission_getter[GETTER_TYPE] = var

    if old_val != SubmissionGetters.TOP.value:
      if var == SubmissionGetters.TOP.value:
        self.__pack_category_frame()
    else:
      if var != SubmissionGetters.TOP.value:
        self.__category_frame.pack_forget()

  def __handle_category_change(self, var:str):
    c: Config = self.application.config
    c.submission_getter[GETTER_CATEGORY] = var

"""
  "number_of_posts": 10,
  "submission_getter": {
    "type": "hot"
  },
  "repeat_hours": 1,
  "repeat_minutes": 0,
  "repeat_seconds": 0,
"""