import time
import threading
from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection
import tkinter as tk
from tkinter import Tk
from tkinter.scrolledtext import ScrolledText
import datetime as dt
from enum import Enum

class Level(Enum):
  INFO = 'Info'
  WARNING = 'Warning'
  ERROR = 'ERROR'


class Logger:
  active: bool
  __connection: Connection
  __process: Process

  def __init__(self, active: bool, connection: Connection,process: Process) -> None:
      self.active = active
      self.__connection = connection
      self.__process = process
  
  def log(self, message: str, lvl: Level = Level.INFO):
    if self.active:
      if not message.endswith("\n"):
        message+="\n"
      time = "[{d}][{ms}] ".format(d = dt.datetime.now().isoformat(sep=" "), ms=lvl.value)
      self.__connection.send(time + message)

  def stop(self):
    try:
      self.__connection.close()
      time.sleep(1)
      self.__process.terminate()
    finally:
      pass
  
def start(verbose: bool,welcome_message:str)-> Logger:
  parent, child = Pipe()
  p = Process(target=__execute,args=(child,welcome_message))
  p.start()
  return Logger(verbose,parent,p)

def __disable_event():
  pass

def __execute(connection: Connection,welcome_message:str):
  window = Tk()
  window.title("Reddit Crawl Logger")
  window.wm_attributes("-topmost", 1)
  window.geometry("800x600")
  window.protocol("WM_DELETE_WINDOW", __disable_event)
  text = ScrolledText(window,width=250,height=150, wrap='word',bg="black", fg="white")
  
  time = "[{d}][{ms}] ".format(d = dt.datetime.now().isoformat(sep=" "), ms=Level.INFO.value)

  text.insert(tk.END,time+welcome_message)
  text.pack(side=tk.LEFT)

  thread = threading.Thread(name="connection monitor", target=__conection_handler, args=(connection,text))
  thread.start()

  tk.mainloop()

def __conection_handler(connection: Connection, text_box: ScrolledText):
  while True:
    try:
      recieved:str = connection.recv()
      text_box.insert(tk.END,recieved)
    except:
      break
