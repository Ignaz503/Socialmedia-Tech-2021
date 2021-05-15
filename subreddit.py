import json
from os import path

SUBREDDIT_FILE = "subreddits.json"

class Subreddit:
  name: str
  sub_count: int

  def __init__(self, name: str, sub_count: int) -> None:
      self.name = name
      self.sub_count = sub_count

  def to_json(self) -> str:
    return json.dumps(self,default=lambda o: o.__dict__,sort_keys=True,indent=4)

SubredditList = list[Subreddit]

class Subreddits:
  data: SubredditList

  def __init__(self, some_data: SubredditList = None) -> None:
    self.data = []

    if some_data is not None:
      for subreddit in some_data["data"]:
        self.data.append(Subreddit(subreddit["name"],subreddit["sub_count"]))
  
  def get_subreddit(self, name: str) -> Subreddit:
    for sub in self.data:
      if sub.name == name:
        return sub
    return None

  def get_or_add_subreddit(self, name: str, count: int) -> Subreddit:
    sub = self.get_subreddit(name)

    if sub is not None:
      return sub

    self.data.append(Subreddit(name, count))
    return self.data[-1]

  def print_subreddit_names(self):
    for sub in self.data:
      print(sub.name)

  def to_json(self) -> str:
    return json.dumps(self,default=lambda o: o.__dict__,sort_keys=True,indent=4)

  def save_to_file(self, file_path: str):
    content = self.to_json()
    with open(file_path, 'w') as f:
      f.write(content)

def load(file_path: str) -> Subreddits:
  if not path.exists(file_path):
    with open(file_path,'w'): pass
    return Subreddits(None)
  else:
    with open(file_path, 'r') as f:
      content = f.read()
      deser = json.loads(content)
      return Subreddits(deser)