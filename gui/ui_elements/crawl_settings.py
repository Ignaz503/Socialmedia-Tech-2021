from tkinter.constants import BOTH, LEFT, TOP, X
from typing import Text
from gui.ui_elements.ui_element import UIElement
from tkinter import Label, ttk

class CrawlSettings(UIElement):
  def __init__(self, application, *args, **kwargs) -> None:
      super().__init__(application, *args, **kwargs)

  def _build(self):
    l = Label(master= self,text="Log",relief="groove")
    #self.__label.grid(row=0,column=0, sticky=NSEW)
    l.pack(fill=X,expand=True, pady=5)

    tab_control = ttk.Notebook(self)

    general_tab = GeneralSettings(application=self.application,master=tab_control)
    tab_control.add(general_tab,text="General")

    active_tab = ActiveCrawlSettings(application=self.application,master=tab_control)
    tab_control.add(active_tab,text="Active Crawl")

    stream_tab = StreamSettings(application=self.application,master=tab_control)
    tab_control.add(stream_tab,text="Stream Observation")

    historic_tab = HistoricSettings(application=self.application,master=tab_control)
    tab_control.add(historic_tab,text="Historic Crawl")

    tab_control.pack(fill=BOTH, side=TOP)


class ActiveCrawlSettings(UIElement):
  def __init__(self, application, *args, **kwargs) -> None:
      super().__init__(application, *args, **kwargs)
  
  def _build(self):
    l = Label(master=self,text="hi active crawl")
    l.pack(side=LEFT,expand=True)
    
class StreamSettings(UIElement):
  def __init__(self, application, *args, **kwargs) -> None:
      super().__init__(application, *args, **kwargs)
  
  def _build(self):
    l = Label(master=self,text="hi stream observation")
    l.pack(side=LEFT,expand=True)

class GeneralSettings(UIElement):
  def __init__(self, application, *args, **kwargs) -> None:
      super().__init__(application, *args, **kwargs)
  
  def _build(self):
    l = Label(master=self,text="hi general settings")
    l.pack(side=LEFT,expand=True)

class HistoricSettings(UIElement):
  def __init__(self, application, *args, **kwargs) -> None:
      super().__init__(application, *args, **kwargs)
  
  def _build(self):
    l = Label(master=self,text="hi historic settings")
    l.pack(side=LEFT,expand=True)