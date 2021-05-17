from io import FileIO
import json
from os import path
import jsonpickle
from jsonpickle.handlers import DatetimeHandler
from os import path

def make_name(base_path: str, sub_name: str) -> str:
  return path.join(base_path, sub_name + ".json")

class Subreddit_Data:
  name:str
  users: set[str]

  def __init__(self, name: str, users: set[str]):
    self.name = name
    self.users = users

  def add_user(self, user_name: str):
    self.users.add(user_name)

  def to_json(self):
    return jsonpickle.encode(self,indent=2)
  
  def save_to_file(self, base_path: str):
    content = self.to_json()
    with open(make_name(base_path,self.name), 'w') as f:
      f.write(content)

def load(base_path: str,name: str) -> Subreddit_Data:
  file_path = make_name(base_path,name)
  if not path.exists(file_path):
    with open(file_path,'w'): pass
    return Subreddit_Data(name,set([]))
  else:
    with open(file_path, 'r') as f:
      content = f.read()
      return jsonpickle.decode(content)


#def generate_subreddit_pair_for_user(self,user_name: str) -> list[tuple[str,str]]:
#todo maybe make this a generator as well
#subs = list(self.data[user_name])
#pairs =[(subs[i],subs[j]) for i in range(len(subs)) for j in range(i+1, len(subs))]
#return  pairs

#def generate_subreddit_pairs_for_all_users(self) -> tuple[str,list[tuple[str,str]]]:
#res: dict[str,tuple[str,str]] = {}
#for user in self.data:
#yield (user, self.generate_subreddit_pair_for_user(user))