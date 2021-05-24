from tkinter import Toplevel
from tkinter.constants import BOTH
from gui.ui_elements.settings.settings_tab_window import SettingsTabControls


class SettingsWindow(Toplevel):
  __tab_control: SettingsTabControls

  def __init__(self,application,*args, **kwargs ) -> None:
    super().__init__(*args,**kwargs)
    self.application = application
    self.__tab_control = None
    self.__build()
  
  def __build(self):
    self.title("Team 1 Reddit Crawl Settings")
    self.__tab_control = SettingsTabControls(application=self.application,master=self)
    self.__tab_control.pack(fill=BOTH,expand=True)