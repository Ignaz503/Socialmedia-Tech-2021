from defines import MAX_NUM_ROWS
import time
import threading
from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection
import tkinter as tk
from tkinter import Tk,font
from tkinter.constants import END
from tkinter.scrolledtext import ScrolledText
import datetime as dt
from enum import IntEnum,Enum
from queue import Queue
from typing import Callable
from os import path
import utility.data_util as data_util

LOG_TEXT = 'text'
LOG_COLOR = 'color'

class Level(Enum):
  INFO = {LOG_TEXT:'Info',LOG_COLOR:'#32cd32'}
  WARNING = {LOG_TEXT:'Warning',LOG_COLOR:'yellow'}
  ERROR = {LOG_TEXT:'ERROR',LOG_COLOR:'red'}

class MessageType(IntEnum):
  LOG = 0
  PATH_UPDATE = 1


class Logger:
  _active: bool
  def __init__(self,active:bool):
    self._active = active

  def _build_header(self, lvl:Level)->str:
    return "[{d}][{ms}] ".format(d = dt.datetime.now().isoformat(sep=" ",timespec='milliseconds'), ms=lvl.value[LOG_TEXT])

  def log(self, message: str, lvl: Level = Level.INFO):
    if self._active:
      print(self._build_header()+message)
  
  def set_active(self, value: bool):
    self._active = value

  def toggle_active(self):
    self._active = not self._active

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

      if not isinstance(message,str):
        message= str(message)

      if not message.endswith("\n"):
        message+="\n"
      time = self._build_header(lvl)
      if not self.__connection.closed:
        self.__connection.send([MessageType.LOG,time + message, lvl])

  def update_log_storage_path(self, new_path:str):
    self.__connection.send([MessageType.PATH_UPDATE,new_path])

  def stop(self):
    try:
      self.__connection.close()
      time.sleep(2)
      self.__process.terminate()
    finally:
      pass

def start(config)-> Sperate_Process_Logger:
  return __start_seperate_process_logger(config)

def __start_seperate_process_logger(config) -> Sperate_Process_Logger:
  parent, child = Pipe()
  p = Process(target=__execute,args=(child,config.get_path_to_storage()))
  p.start()
  return Sperate_Process_Logger(parent,p,active=config.verbose)

def __disable_event():
  pass

def __execute(connection: Connection, base_path:str):
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


  thread = threading.Thread(name="connection monitor", target=__conection_handler, args=(connection,text,base_path))
  thread.start()
  tk.mainloop()

def __conection_handler(connection: Connection, text_box: ScrolledText,base_path:str):
  while True:
    try:
      recieved:str = connection.recv()
      if recieved[0] == MessageType.LOG:
        __display(recieved[1],recieved[2],text_box,base_path)
      if recieved[0] == MessageType.PATH_UPDATE:
        base_path = recieved[1]
    except:
      __save_log(text_box,base_path)
      break

def __display(message:str, level: Level, text: ScrolledText,base_path:str):
  row_idx_start = int(text.index(END).split(".")[0])-1
  start_sel =f"{row_idx_start}.0"    

  text.insert(END,message)

  row_idx_end =int(text.index(END).split(".")[0])-1
  if row_idx_end - row_idx_start == 1:
    row_idx_end = row_idx_start

  end = len(message)-1
  end_sel = f"{row_idx_end}.{end}"
  text.tag_add(level.value[LOG_TEXT],start_sel,end_sel)
  __try_save_log_and_clear(text,base_path)
  text.after(250,lambda:__scroll_to_bottom(text))

def __scroll_to_bottom(text: ScrolledText):
  y = text.yview()
  if(y[1] < 1.0):
    text.yview_moveto(y[1]+0.0000001*0.016)
    text.after(100,lambda: __scroll_to_bottom(text))

def __try_save_log_and_clear(text:ScrolledText,base_path:str):
  current_row = int(text.index(END).split(".")[0])
  if current_row >= MAX_NUM_ROWS:
    __save_log(text,base_path)
    text.delete("1.0",END)

def __save_log(text: ScrolledText, base_path:str):
  log_so_far = text.get("1.0",END)
  with open(data_util.make_data_path_str(base_path,f"log {dt.date.today().isoformat()}.txt",data_util.DataLocation.LOG),'a',encoding="utf-8") as f:
    f.write(log_so_far)