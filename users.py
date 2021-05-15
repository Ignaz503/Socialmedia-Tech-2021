from io import FileIO
import json
from os import path

USER_FILE = "users.json"

class User:
  name: str
  subreddtis: list[str]
  def __init__(self, name:str, subreddit: str = None) -> None:
    self.name = name
    self.subreddtis = []
    if subreddit is not None:
      self.subreddtis.append(subreddit)
  
  def try_add_subreddit(self, subreddit: str) -> bool:
    if not subreddit in self.subreddtis:
      self.subreddtis.append(subreddit)
      return True
    return False

  def generate_subreddit_pairs(self) -> list[str]:
    pairs =[(self.subreddtis[i],self.subreddtis[j]) for i in range(len(self.subreddtis)) for j in range(i+1, len(self.subreddtis))]
    return  pairs

  def to_json(self) -> str:
      return json.dumps(self,default=lambda o: o.__dict__,sort_keys=True,indent=4)

UserList = list[User]

class Users:
  data: UserList
 
  def __init__(self, data = None):
    self.data = []
    if data is not None:
      for user in data["data"]:
        self.data.append(User(user["name"],user["subreddtis"]))


  def get_or_add_user(self, user_name: str, subreddit: str = None) -> User:
    for user in self.data:
      if user.name == user_name:
        if subreddit is not None:
          user.try_add_subreddit(subreddit)
        return user
    self.data.append(User(user_name,subreddit))
    return self.data[-1]
  
  def to_json(self):
    return json.dumps(self,default=lambda o: o.__dict__,sort_keys=True,indent=4)
  
  def print_user_names(self):
    for user in self.data:
      print(user.name)

  def save_to_file(self, file_path: str):
    content = self.to_json()
    with open(file_path, 'w') as f:
      f.write(content)


def load(file_path: str) -> Users:
  if not path.exists(file_path):
    with open(file_path,'w'): pass
    return Users(None)
  else:
    with open(file_path, 'r') as f:
      content = f.read()
      deser = json.loads(content)
      return Users(deser)