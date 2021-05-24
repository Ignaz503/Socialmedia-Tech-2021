from tkinter import Menu
from tkinter.constants import BOTH
from gui.ui_elements.windows.settings_window import SettingsWindow

class MenuBar(Menu):

  def __init__(self,application, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.__application = application
    self.__build()

  def __build(self):
    tool_menu = Menu(self,tearoff=0)
    tool_menu.add_command(label="Settings", command=lambda: self.__show_settings())
    self.add_cascade(label="Tool",menu=tool_menu)

  def __show_settings(self):
    SettingsWindow(application = self.__application,master = self.master)




