import jsonpickle
from os import path
from threading import Lock

class Bot_Blacklist:
  blacklist: set[str]

  def __init__(self, blacklist: set[str]) -> None:
      self.blacklist = blacklist

  def to_json(self):
    return jsonpickle.encode(self, indent=2)

  def save_to_file(self, file_path: str):
    content = self.to_json()
    with open(file_path, 'w') as f:
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

  def save_to_file(self, file_path: str):
    self.data.save_to_file(file_path)

def load(file_path) -> Threadsafe_Bot_Blacklist:
  if not path.exists(file_path):
    with open(file_path,'w'): pass
    return Threadsafe_Bot_Blacklist(Bot_Blacklist(set([])))
  else:
    with open(file_path, 'r') as f:
      content = f.read()
      return Threadsafe_Bot_Blacklist(jsonpickle.decode(content))
