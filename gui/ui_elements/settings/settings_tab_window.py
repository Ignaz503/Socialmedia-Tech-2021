from tkinter.constants import BOTH, LEFT, TOP, X
from typing import Text
from gui.ui_elements.ui_element import UIElement
from tkinter import Label, ttk
from gui.ui_elements.settings.historic_crawl_settings import HistoricSettings
from gui.ui_elements.settings.general_app_settings import GeneralSettings
from gui.ui_elements.settings.stream_observation_settings import StreamSettings
from gui.ui_elements.settings.active_crawl_settings import ActiveCrawlSettings
from enum import Enum

class SettingsTabs(Enum):
  GENERAL = 0
  ACTIVE_CRAWL = 1
  STREAM = 2
  HISTORIC = 3

class SettingsTabControls(UIElement):
  
  __tab_control: ttk.Notebook

  def __init__(self, application, *args, **kwargs) -> None:
    self.__tab_control = None
    super().__init__(application, *args, **kwargs)

  def _build(self):
    l = Label(master= self,text="Settings",relief="groove")
    #self.__label.grid(row=0,column=0, sticky=NSEW)
    l.pack(fill=X,expand=True, pady=5)

    self.__tab_control = ttk.Notebook(self)

    general_tab = GeneralSettings(application=self.application,master=self.__tab_control)
    self.__tab_control.add(general_tab,text="General")

    active_tab = ActiveCrawlSettings(application=self.application,master=self.__tab_control)
    self.__tab_control.add(active_tab,text="Active Crawl")

    stream_tab = StreamSettings(application=self.application,master=self.__tab_control)
    self.__tab_control.add(stream_tab,text="Stream Observation")

    historic_tab = HistoricSettings(application=self.application,master=self.__tab_control)
    self.__tab_control.add(historic_tab,text="Historic Crawl")

    self.__tab_control.pack(fill=BOTH, side=TOP)
   
  def show_tab(self,tab: SettingsTabs):
    self.__tab_control.select(tab.value)




