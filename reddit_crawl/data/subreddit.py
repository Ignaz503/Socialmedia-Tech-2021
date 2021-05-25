from utility.app_config import Config
import utility.data_util as data_util
import jsonpickle
from threading import Lock
from utility.simple_logging import Logger, Level
from utility.data_util import DataLocation
import math
import datetime as dt
import textwrap

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

  def contains(self, user_name: str)->bool:
    return user_name in self.users

  def to_json(self):
    return jsonpickle.encode(self,indent=2)
  
  def save_to_file(self, config: Config):
    content = self.to_json()   
    with open(data_util.make_data_path(config,self.name + ".json",DataLocation.SUBREDDIT), 'w') as f:
      f.write(content)

  def __iter__(self):
    for user in self.users:
      yield user

  def __contains__(self, item):
    return item in self.users

  @staticmethod
  def load(subbredit_name: str, config:Config):
    filename = subbredit_name + ".json"
    if data_util.file_exists(config,filename, DataLocation.SUBREDDIT):
      with open(data_util.make_data_path(config,filename, DataLocation.SUBREDDIT), 'r') as f:
        content = f.read()
        return jsonpickle.decode(content)
    return Subreddit_Data(subbredit_name,set([]))

class Subreddit_Batch:
  subs: dict[str, Subreddit_Data]

  def __init__(self) -> None:
    self.subs = {}

  def add_user(self, sub_name: str, user_name: str):
    if sub_name in self.subs:
      return self.subs[sub_name].add_user(user_name)
    self.subs[sub_name] = Subreddit_Data(sub_name,set([user_name]))
    return True

  def conatins_user(self, user_name:str, subreddit_name:str)->bool:
    if subreddit_name in self.subs:
      return user_name in self.subs[subreddit_name]

  def __handle_data(self, sub_name: str, data: Subreddit_Data,config:Config, logger: Logger):
    logger.log("-"*30,Level.INFO)
    logger.log("Loading data for {s}".format(s=sub_name),Level.INFO)
    current: Subreddit_Data = Subreddit_Data.load(sub_name,config)
    logger.log("Updating data for {s}".format(s=sub_name),Level.INFO)
    current.add_users(data.users) 
    logger.log("Saving {s} to disk".format(s=sub_name),Level.INFO)
    current.save_to_file(config)
    logger.log("-"*30, Level.INFO)

  def save_to_file(self,config:Config, logger: Logger):
    for sub in  self.subs:
      self.__handle_data(sub,self.subs[sub],config, logger)

class Subreddit_Batch_Queue:
  lock: Lock
  batch_queue: list[Subreddit_Batch]

  def __init__(self) -> None:
    self.batch_queue = []
    self.lock = Lock()

  def enqueue(self, batch: Subreddit_Batch):
    with self.lock:
      self.batch_queue.append(batch)
  
  def update(self,config:Config, logger: Logger):
    batch = None
    while len(self.batch_queue) > 0:
      leng = len(self.batch_queue)
      logger.log("{l} batches in queue to handle".format(l = leng), Level.INFO)
      with self.lock:
        batch = self.batch_queue.pop(0)
      self.__store_batch(batch,config, logger)

  def handle_all(self,config:Config, logger: Logger):
    for batch in self.batch_queue:
      self.__store_batch(batch,config, logger)

  def __store_batch(self, batch: Subreddit_Batch,config:Config, logger: Logger):
    if batch is None:
      return
    batch.save_to_file(config,logger)
    del batch
  
class Subreddit_Metadata:
  subscriber_count: int
  description: str
  created_utc: float

  def __init__(self,subscriber_count: int, description:str,created_utc:float) -> None:
      self.subscriber_count =subscriber_count
      self.description = description
      self.created_utc = created_utc
  
  def get_creation_time(self) -> dt.datetime:
    return dt.datetime.fromtimestamp(self.created_utc)

  def to_html_string(self):
    date = self.get_creation_time()
    string = "<b>created on:</b> {d}".format(d=date.isoformat(sep=" "))+'<br>'
    string += "<b>subscriber count:</b> {c}".format(c=self.subscriber_count) + '<br>'
    string += "<b>description:</b><br>"
    desc = '<br>'.join(textwrap.wrap(self.description,50))
    return string + desc

class Crawl_Metadata: 
  __FILE_NAME = "subreddit_metadata.json"
  data: dict[str,Subreddit_Metadata]
  larges_sub: str
  smallest_sub: str

  def __init__(self, data: dict[str,Subreddit_Metadata], largest:str, smallest:str) -> None:
      self.data = data
      self.larges_sub = largest
      self.smallest_sub = smallest

  def add_meta_data(self,sub_name: str, meta: Subreddit_Metadata, update: bool = True):
    if  sub_name in self.data and not update:
      return
    self.data[sub_name] = meta
    if self.get_smallest_sub_count() > meta.subscriber_count:
      self.smallest_sub = sub_name
    if self.get_largest_sub_count() < meta.subscriber_count:
      self.larges_sub = sub_name

  def get_largest_sub_count(self) -> int:
    if self.larges_sub not in self.data:
      return -1
    return self.data[self.larges_sub].subscriber_count

  def get_smallest_sub_count(self) -> int:
    if self.smallest_sub not in self.data:
      return 2 ** 64 #int uncapped so just return some ridiculous huge data
    return self.data[self.smallest_sub].subscriber_count

  def get_sub_count(self, sub_name: str):
    if sub_name not in self.data:
      return 0
    return self.data[sub_name].subscriber_count

  def lerp_sub_count(self, sub_name: str, logger: Logger)-> float:
    if sub_name not in self.data:
      logger.log("{s} not found in meta data".format(s=sub_name),Level.WARNING)
      return 0.5

    size = float(self.data[sub_name].subscriber_count)
    small = float(self.get_smallest_sub_count())
    large = float(self.get_largest_sub_count())
    divisor = large - small

    if math.isclose(divisor,0.0):
      return 0.5#idk maybe something else
    return (size - small) / divisor

  def to_json(self) -> str:
    return jsonpickle.encode(self, indent=2)
  
  def save_to_file(self,config:Config):
    content = self.to_json()   
    with open(data_util.make_data_path(config,Crawl_Metadata.__FILE_NAME,DataLocation.SUBREDDIT_META), 'w') as f:
      f.write(content)

  @staticmethod
  def load(config:Config):
    if data_util.file_exists(config,Crawl_Metadata.__FILE_NAME,DataLocation.SUBREDDIT_META):
      with open(data_util.make_data_path(config,Crawl_Metadata.__FILE_NAME,DataLocation.SUBREDDIT_META),'r') as f:
        content = f.read()
        return jsonpickle.decode(content)
    return Crawl_Metadata.empty()
  
  @staticmethod
  def empty():
    return Crawl_Metadata({},"","")