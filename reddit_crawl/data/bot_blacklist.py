from utility.app_config import Config
import utility.data_util as data_util
import jsonpickle
from threading import Lock
from utility.data_util import DataLocation

class Bot_Blacklist:
  blacklist: set[str]

  def __init__(self, blacklist: set[str]) -> None:
      self.blacklist = blacklist

  def to_json(self):
    return jsonpickle.encode(self, indent=2)

  def save_to_file(self, filename: str, config:Config):
    content = self.to_json()   
    with open(data_util.make_data_path(config,filename,DataLocation.DEFAULT), 'w') as f:
      f.write(content)

class Threadsafe_Bot_Blacklist:
  data: Bot_Blacklist
  lock: Lock
  def __init__(self, list: Bot_Blacklist) -> None:
      self.data = list
      self.lock = Lock()
  
  def add(self,new_bot: str):
    with self.lock:
      self.data.blacklist.add(new_bot)
  
  def contains(self, name: str) -> bool:
    with self.lock:
      return name in self.data.blacklist

  def save_to_file(self, file_path: str, config:Config):
    self.data.save_to_file(file_path,config)

def load(filename, config:Config) -> Threadsafe_Bot_Blacklist:
  if data_util.file_exists(config,filename, DataLocation.DEFAULT):
    with open(data_util.make_data_path(config,filename, DataLocation.DEFAULT), 'r') as f:
      content = f.read()
      return Threadsafe_Bot_Blacklist(jsonpickle.decode(content))
  return Threadsafe_Bot_Blacklist(Bot_Blacklist(set([])))
