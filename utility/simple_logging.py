import time
import threading
from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection
import tkinter as tk
from tkinter import Tk,font
from tkinter.constants import END
from tkinter.scrolledtext import ScrolledText
import datetime as dt
from enum import Enum
from queue import Queue
from typing import Callable

LOG_TEXT = 'text'
LOG_COLOR = 'color'

class Level(Enum):
  INFO = {LOG_TEXT:'Info',LOG_COLOR:'#32cd32'}
  WARNING = {LOG_TEXT:'Warning',LOG_COLOR:'yellow'}
  ERROR = {LOG_TEXT:'ERROR',LOG_COLOR:'red'}

class Logger:
  _active: bool
  def __init__(self,active:bool):
    self._active = active

  def _build_header(self, lvl:Level)->str:
    return "[{d}][{ms}] ".format(d = dt.datetime.now().isoformat(sep=" ",timespec='milliseconds'), ms=lvl.value[LOG_TEXT])

  def log(self, message: str, lvl: Level = Level.INFO):
    if self._active:
      print(self._build_header()+message)
  
  def stop(self):
    pass

class Sperate_Process_Logger(Logger):
  __connection: Connection
  __process: Process

  def __init__(self,connection: Connection,process: Process,*args,**kwargs) -> None:
      super().__init__(*args,**kwargs)
      self.__connection = connection
      self.__process = process
  
  def log(self, message: str, lvl: Level = Level.INFO):
    if self._active:
      if not message.endswith("\n"):
        message+="\n"
      time = self._build_header(lvl)
      self.__connection.send([time + message, lvl])

  def stop(self):
    try:
      self.__connection.close()
      time.sleep(1)
      self.__process.terminate()
    finally:
      pass

def start(verbose: bool)-> Logger:
  return __start_seperate_process_logger(verbose)

def __start_seperate_process_logger(verbose: bool) -> Sperate_Process_Logger:
  parent, child = Pipe()
  p = Process(target=__execute,args=(child,))
  p.start()
  return Sperate_Process_Logger(parent,p,active=verbose)

def __disable_event():
  pass

def __execute(connection: Connection):
  window = Tk()
  window.title("Reddit Crawl Logger")
  #window.wm_attributes("-topmost", 1)
  window.geometry("800x240")
  window.protocol("WM_DELETE_WINDOW", __disable_event)
  text = ScrolledText(window,width=250,height=150, wrap='word',bg="black", fg="white")
  
  text.pack(side=tk.LEFT)

  color_font = font.Font(text, text.cget("font"))
  text.tag_configure(
    Level.INFO.value[LOG_TEXT],
      font=color_font,
      foreground=Level.INFO.value[LOG_COLOR])
  text.tag_configure(
    Level.WARNING.value[LOG_TEXT],
      font=color_font,
      foreground=Level.WARNING.value[LOG_COLOR])
  text.tag_configure(
    Level.ERROR.value[LOG_TEXT],
      font=color_font,
      foreground=Level.ERROR.value[LOG_COLOR])


  thread = threading.Thread(name="connection monitor", target=__conection_handler, args=(connection,text))
  thread.start()
  tk.mainloop()

def __conection_handler(connection: Connection, text_box: ScrolledText):
  while True:
    try:
      recieved:str = connection.recv()
      __display(recieved[0],recieved[1],text_box)
    except:
      break

def __display(message:str, level: Level, text: ScrolledText):
  row_idx_start = int(text.index(END).split(".")[0])-1
  start_sel =f"{row_idx_start}.0"    

  text.insert(END,message)

  row_idx_end =int(text.index(END).split(".")[0])-1
  if row_idx_end - row_idx_start == 1:
    row_idx_end = row_idx_start

  end = len(message)-1
  end_sel = f"{row_idx_end}.{end}"
  text.tag_add(level.value[LOG_TEXT],start_sel,end_sel)

  text.after(250,lambda:__scroll_to_bottom(text))

def __scroll_to_bottom(text: ScrolledText):
  y = text.yview()
  if(y[1] < 1.0):
    text.yview_moveto(y[1]+0.0000001*0.016)
    text.after(100,lambda: __scroll_to_bottom(text))