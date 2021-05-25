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
    with open(data_util.make_data_path(config,UniqueUsers.__FILE_NAME,DataLocation.SUBREDDIT_META), 'w') as f:
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
    if data_util.file_exists(config,UniqueUsers.__FILE_NAME, DataLocation.SUBREDDIT_META):
      with open(data_util.make_data_path(config,UniqueUsers.__FILE_NAME, DataLocation.SUBREDDIT_META), 'r') as f:
        content = f.read()
        return jsonpickle.decode(content)
    return UniqueUsers(set([]))