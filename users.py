from io import FileIO
import json
from os import path
import jsonpickle
from jsonpickle.handlers import DatetimeHandler

FILE = "users.json"

class Users:
  data: dict[str,set[str]]
 
  def __init__(self, data = None):
    if data is None:
      self.data = {}
    else:
      self.data = data

  def add_user(self, user_name: str):
    if user_name not in self.data:
      self.data[user_name] = set([])

  def add_user_init(self, user_name:str, subreddit:str):
    if user_name not in self.data:
      self.add_user(user_name)
    self.data[user_name].add(subreddit)
  
  def add_subreddit_for_user(self, user_name: str, subreddit: str):
    if user_name not in self.data:
      self.add_user(user_name)
    self.data[user_name].add(subreddit)

  def generate_subreddit_pair_for_user(self,user_name: str) -> list[tuple[str,str]]:
    #todo maybe make this a generator as well
    subs = list(self.data[user_name])
    pairs =[(subs[i],subs[j]) for i in range(len(subs)) for j in range(i+1, len(subs))]
    return  pairs

  def generate_subreddit_pairs_for_all_users(self) -> tuple[str,list[tuple[str,str]]]:
    res: dict[str,tuple[str,str]] = {}
    for user in self.data:
      yield (user, self.generate_subreddit_pair_for_user(user))


  def to_json(self):
    return jsonpickle.encode(self,indent=2)
  
  def save_to_file(self, file_path: str):
    content = self.to_json()
    with open(file_path, 'w') as f:
      f.write(content)

  def print_user_names(self):
    for user in self.data:
      print(user)

def load(file_path: str) -> Users:
  if not path.exists(file_path):
    with open(file_path,'w'): pass
    return Users(None)
  else:
    with open(file_path, 'r') as f:
      content = f.read()
      return jsonpickle.decode(content)