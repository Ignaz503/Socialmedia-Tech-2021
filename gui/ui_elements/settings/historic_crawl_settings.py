from tkinter import Frame, LEFT, Label, StringVar
from tkinter.constants import TOP, X
from utility.app_config import Config
from gui.ui_elements.ui_element import UIElement
from gui.ui_elements.input_box import EnterAcceptInputBox
import datetime as dt

class HistoricSettings(UIElement):

  __from_date_var: StringVar
  __to_date_var: StringVar

  def __init__(self, *args, **kwargs) -> None:
    self.__from_date_var = StringVar()
    self.__to_date_var = StringVar()
    super().__init__(*args, **kwargs)
  
  def _build(self):
    c: Config = self.application.config

    from_frame = Frame(master = self,relief="groove",borderwidth=1)
    from_frame.pack(side=TOP,fill=X, pady=5, expand=True)

    l = Label(master=from_frame,text="From: ")
    l.pack(side=LEFT,expand=True)

    self.__from_date_var.set(c.from_date)

    input_box = EnterAcceptInputBox(on_accept=lambda e: self.__parse_from_date(),
      focus_target=self.master,
      master=from_frame,
      textvariable=self.__from_date_var)
    input_box.configure(
      validate="focusout",
      validatecommand= self.__parse_from_date)
    input_box.pack(side=LEFT,fill=X,padx=5,expand=True)

    to_frame = Frame(master = self,relief="groove",borderwidth=1)
    to_frame.pack(side=TOP,fill=X, pady=5, expand=True)

    l = Label(master=to_frame,text="To: ")
    l.pack(side=LEFT,expand=True)

    self.__to_date_var.set(c.to_date)

    input_box = EnterAcceptInputBox(on_accept=lambda e: self.__parse_to_date(),
      focus_target=self.master,
      master=to_frame,
      textvariable=self.__to_date_var)
    input_box.configure(
      validate="focusout",
      validatecommand= self.__parse_to_date)
    input_box.pack(side=LEFT,fill=X,padx=5,expand=True)


  def __parse_from_date(self):
    try:
      date = dt.date.fromisoformat(self.__from_date_var.get())
      self.application.set_config_value('from_date',self.__from_date_var.get())
    except ValueError:
      self.__from_date_var.set(self.application.config.from_date)

  def __parse_to_date(self):
    try:
      date = dt.date.fromisoformat(self.__to_date_var.get())
      self.application.set_config_value('to_date',self.__to_date_var.get())
    except ValueError:
      self.__to_date_var.set(self.application.config.to_date)


"""
  "from_date": "2021-04-01",
  "to_data": "2021-05-19",
"""