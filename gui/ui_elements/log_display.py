import tkinter as tk
from tkinter import Frame,Label, NSEW
from tkinter.constants import E, EW, NS, X
from tkinter.scrolledtext import ScrolledText
from gui.ui_elements.ui_element import UIElement

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
    self.__log_display = ScrolledText(master=self, wrap='word',bg="black", fg="white",takefocus=False,width=100,height=10)
    #self.__log_display.grid(row=1,column=0)
    self.__log_display.pack(fill=X,expand=True)
  
  def display(self,message: str):
    self.__log_display.insert(tk.END,message)
