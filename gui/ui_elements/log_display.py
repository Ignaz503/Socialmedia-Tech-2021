import tkinter as tk
from tkinter import Frame,Label, NSEW, Tk
from tkinter.constants import CURRENT, E, EW, NS, X,END
from tkinter.scrolledtext import ScrolledText
from utility.simple_logging import LOG_COLOR, LOG_TEXT, Level
from gui.ui_elements.ui_element import UIElement
from tkinter import font

class Logging_Frame(UIElement): 
  __label: Label
  __log_display: ScrolledText
  def __init__(self,*args,**kwargs) -> None:
    self.__label = None
    self.__log_display = None

    super().__init__(*args,**kwargs)

  def _build(self) -> None:
    self.__label = Label(master= self,text="Log",relief="groove")
    #self.__label.grid(row=0,column=0, sticky=NSEW)
    self.__label.pack(fill=X,expand=True, pady=5)
    self.__log_display = ScrolledText(master=self, wrap='word',bg="black",fg="white",takefocus=False,width=100,height=10)
    #self.__log_display.grid(row=1,column=0)
    self.__log_display.pack(fill=X,expand=True)

    color_font = font.Font(self.__log_display, self.__log_display.cget("font"))
    self.__log_display.tag_configure(
      Level.INFO.value[LOG_TEXT],
       font=color_font,
       foreground=Level.INFO.value[LOG_COLOR])
    self.__log_display.tag_configure(
      Level.WARNING.value[LOG_TEXT],
       font=color_font,
       foreground=Level.WARNING.value[LOG_COLOR])
    self.__log_display.tag_configure(
      Level.ERROR.value[LOG_TEXT],
       font=color_font,
       foreground=Level.ERROR.value[LOG_COLOR])
  
  def display(self,message: str, level: Level):
    row_idx_start = int(self.__log_display.index(END).split(".")[0])-1
    start_sel =f"{row_idx_start}.0"    

    self.__log_display.insert(END,message)

    row_idx_end =int(self.__log_display.index(END).split(".")[0])-1
    if row_idx_end - row_idx_start == 1:
      row_idx_end = row_idx_start

    end = len(message)-1
    end_sel = f"{row_idx_end}.{end}"
    self.__log_display.tag_add(level.value[LOG_TEXT],start_sel,end_sel)

    self.after(250,lambda:self.__scroll_to_bottom())

  def __scroll_to_bottom(self):
    y = self.__log_display.yview()
    if(y[1] < 1.0):
      self.__log_display.yview_moveto(y[1]+0.0000001*0.016)
      self.after(100,lambda: self.__scroll_to_bottom())
    

    
