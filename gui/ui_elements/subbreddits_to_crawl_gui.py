from tkinter import Frame,Label, Widget
from tkinter.constants import BOTH, CENTER, LEFT, N, END, NS, W
from tkinter.scrolledtext import ScrolledText
from utility.app_config import Config
from gui.ui_elements.ui_element import UIElement

class Subbredits_To_Crawl_GUI(UIElement): 
  def __init__(self, *args, **kwargs) -> None:
      self.__label = None
      self.__input_box = None
      super().__init__(*args,**kwargs)

  def _build(self) -> None:
    self.__label = Label(master= self,text="Subbredits to crawl")
    self.__label.pack(side=LEFT,anchor=CENTER,padx=5,pady=5,expand=True)
    self.__input_box = ScrolledText(master=self, wrap='word', width=20,height=5)
    self.__input_box.pack(fill=BOTH,pady=5,padx=5,expand=True)
    self.__input_box.bind('<Return>',lambda event: self.__update_subreddits())
    self.__input_box.bind('<FocusOut>',lambda e: self.__update_subreddits())

    c: Config = self.application.config
    subs = "\n".join(c.subreddits_to_crawl)
    self.__input_box.insert(END,subs)

  def get_subbredits(self) -> str:
    string = self.__input_box.get("1.0",END)
    list = string.split("\n")
    while '' in list: 
      list.remove('')
    return list

  def __update_subreddits(self):
    self.application.log("updaing list")
    subs = self.get_subbredits()
    self.application.set_config_value("subreddits_to_crawl",subs)