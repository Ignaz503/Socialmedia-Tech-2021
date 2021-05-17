import jsonpickle
from os import path
FILE ="bot_list.json"

class Bot_Blacklist:
  blacklist: set[str]

  def __init__(self, blacklist: set[str]) -> None:
      self.blacklist = blacklist

  def to_json(self):
    return jsonpickle.encode(self, indent=2)

  def add(self,new_bot: str):
    self.blacklist.add(new_bot)
  
  def contains(self, name: str) -> bool:
    return name in self.blacklist

  def save_to_file(self, file_path: str):
    content = self.to_json()
    with open(file_path, 'w') as f:
      f.write(content)


def load(file_path) -> Bot_Blacklist:
  if not path.exists(file_path):
    with open(file_path,'w'): pass
    return Bot_Blacklist(set([]))
  else:
    with open(file_path, 'r') as f:
      content = f.read()
      return jsonpickle.decode(content)
