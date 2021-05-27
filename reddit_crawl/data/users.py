from typing import Iterable

from networkx.convert_matrix import to_pandas_adjacency
from utility.app_config import Config
import jsonpickle
import utility.data_util as data_util
from utility.data_util import DataLocation


class UniqueUsers:
  __FILE_NAME = "unique_users.json"
  data: set[str]
  def __init__(self, data: set[str]) -> None:
      self.data = data

  def to_json(self):
    return jsonpickle.encode(self,indent=2)
  
  def save_to_file(self, config: Config):
    content = self.to_json()   
    with open(data_util.make_data_path(config,UniqueUsers.__FILE_NAME,DataLocation.METADATA), 'w') as f:
      f.write(content)
  
  def add_user(self, user_name: str):
    self.data.add(user_name)

  def add_users(self, users: set[str]):
    self.data.update(users)

  def count(self):
    return len(self.data)

  def __iter__(self):
    for user in self.data:
      yield user

  def __contains__(self, item):
    return item in self.data

  @staticmethod
  def load(config: Config):
    if data_util.file_exists(config,UniqueUsers.__FILE_NAME, DataLocation.METADATA):
      with open(data_util.make_data_path(config,UniqueUsers.__FILE_NAME, DataLocation.METADATA), 'r') as f:
        content = f.read()
        return jsonpickle.decode(content)
    return UniqueUsers(set([]))


class MultiSubredditUsers:
  __FILE_NAME = "multi_subreddit_users.json"
  data: dict[str,set[str]]
  def __init__(self, data) -> None:
      self.data = data

  def to_json(self):
    return jsonpickle.encode(self,indent=2)

  def get(self, user_name:str):
    return self.data.get(user_name)

  def add_or_update_user(self, user_name:str, subs: Iterable[str]):
    if user_name in self.data:
      self.data[user_name].update(subs)
    else:
      self.data[user_name]= set(subs)

  def __str__(self) -> str:
      return self.to_json()

  def __iter__(self):
    for user in self.data:
      yield (user,self.data[user])    

  def save_to_file(self,config: Config):
    content = self.to_json()   
    with open(data_util.make_data_path(config,MultiSubredditUsers.__FILE_NAME,DataLocation.METADATA), 'w') as f:
      f.write(content)

  @staticmethod
  def load(config: Config):
    if data_util.file_exists(config,MultiSubredditUsers.__FILE_NAME, DataLocation.METADATA):
      with open(data_util.make_data_path(config,MultiSubredditUsers.__FILE_NAME, DataLocation.METADATA), 'r') as f:
        content = f.read()
        return jsonpickle.decode(content)
    return MultiSubredditUsers({})
