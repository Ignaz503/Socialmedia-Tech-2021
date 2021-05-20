from os import path
import jsonpickle
from os import path
from defines import DATA_BASE_PATH
from threading import Lock
from simple_logging import Logger
from util import make_data_path


class Subreddit_Data:
  name:str
  users: set[str]

  def __init__(self, name: str, users: set[str]):
    self.name = name
    self.users = users

  def add_user(self, user_name: str) -> bool:
    contained = user_name in self.users
    self.users.add(user_name)
    return not contained

  def add_users(self, users: set[str]):
    self.users.update(users)

  def to_json(self):
    return jsonpickle.encode(self,indent=2)
  
  def save_to_file(self):
    content = self.to_json()
    
    with open(make_data_path(self.name + ".json"), 'w') as f:
      f.write(content)

def load(name: str) -> Subreddit_Data:
  file_path = make_data_path(name + ".json")
  if not path.exists(file_path):
    with open(file_path,'w'): pass
    return Subreddit_Data(name,set([]))
  else:
    with open(file_path, 'r') as f:
      content = f.read()
      return jsonpickle.decode(content)

class Subreddit_Batch:
  subs: dict[str, Subreddit_Data]

  def __init__(self) -> None:
    self.subs = {}

  def add_user(self, sub_name: str, user_name: str):
    if sub_name in self.subs:
      return self.subs[sub_name].add_user(user_name)
    self.subs[sub_name] = Subreddit_Data(sub_name,set([user_name]))
    return True

  def __handle_data(self, sub_name: str, data: Subreddit_Data, logger: Logger):
    logger.log("-"*30)
    logger.log("Loading data for {s}".format(s=sub_name))
    current = load(sub_name)
    logger.log("Updating data for {s}".format(s=sub_name))
    current.add_users(data.users) 
    logger.log("Saving {s} to disk".format(s=sub_name))
    current.save_to_file()
    logger.log("-"*30)

  def save_to_file(self, logger: Logger):
    for sub in  self.subs:
      self.__handle_data(sub,self.subs[sub], logger)


class Subreddit_Batch_Queue:
  lock: Lock
  batch_queue: list[Subreddit_Batch]

  def __init__(self) -> None:
    self.batch_queue = []
    self.lock = Lock()

  def enqueue(self, batch: Subreddit_Batch):
    with self.lock:
      self.batch_queue.append(batch)
  
  def update(self,logger: Logger):
    batch = None
    while len(self.batch_queue) > 0:
      leng = len(self.batch_queue)
      logger.log("{l} batches in queue to handle".format(l = leng))
      with self.lock:
        batch = self.batch_queue.pop(0)
      self.__store_batch(batch, logger)

  def handle_all(self, logger: Logger):
    for batch in self.batch_queue:
      self.__store_batch(batch, logger)

  def __store_batch(self, batch: Subreddit_Batch, logger: Logger):
    if batch is None:
      return
    batch.save_to_file(logger)
    del batch