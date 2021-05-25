import jsonpickle
from os import path
import os
import datetime as dt
import reddit_crawl.util.submission_getters as submission_getters
from reddit_crawl.util.submission_getters import SubmissionsGetter, SubmissionGetters
from defines import BOT_LIST_FALLBACK, GETTER_TYPE

class NoConfigExists(Exception):
  def __init__(self,name:str,  *args: object) -> None:
      super().__init__("No app config file with {n} exists".format(n=name), *args)

class Config:
  reddit_app_info: dict[str,str]
  subreddits_to_crawl: list[str]
  number_of_posts: int
  submission_getter:dict[str,str]
  verbose: bool
  repeat_seconds:int
  repeat_minutes:int
  repeat_hours:int
  batch_save_interval_seconds:int
  stream_save_interval_seconds:int
  from_date: str
  to_date: str
  path_to_storage:str
  bot_list_name:str
  def __init__(self,  reddit_app_info: dict[str,str],
                      subreddits_to_crawl: list[str],
                      number_of_posts: int,
                      submission_getter:dict[str,str],
                      verbose: bool,
                      repeat_seconds:int,
                      repeat_minutes:int,
                      repeat_hours:int,
                      batch_save_interval_seconds:int,
                      stream_save_interval_seconds:int,
                      from_date: str,
                      to_date: str,
                      path_to_storage:str,
                      bot_list_name:str) -> None:
      self.reddit_app_info = reddit_app_info
      self.subreddits_to_crawl = subreddits_to_crawl
      self.number_of_posts = number_of_posts
      self.submission_getter = submission_getter
      self.verbose = verbose
      self.repeat_hours = repeat_hours
      self.repeat_minutes = repeat_minutes
      self.repeat_seconds = repeat_seconds
      self.batch_save_interval_seconds = batch_save_interval_seconds
      self.stream_save_interval_seconds = stream_save_interval_seconds
      self.from_date = from_date
      self.to_date = to_date
      self.path_to_storage = path_to_storage
      self.bot_list_name = bot_list_name
  
  def get_submission_getter(self) -> SubmissionsGetter:
    return submission_getters.create_gettter(self.submission_getter)

  def get_repeat_time_in_seconds(self):
    return self.repeat_seconds + (self.repeat_minutes*60) + (self.repeat_hours * 60 * 60)

  def start_epoch(self)-> int:
    from_d = dt.date.fromisoformat(self.from_date)
    from_dt = dt.datetime(from_d.year,from_d.month,from_d.day,0,0,0)
    return int(from_dt.timestamp())

  def end_epoch(self):
    to_d = dt.date.fromisoformat(self.to_date)
    to_dt = dt.datetime(to_d.year,to_d.month,to_d.day,23,59,59)
    return int(to_dt.timestamp())

  def to_json(self):
    return jsonpickle.encode(self, indent=2, unpicklable=False)

  def __str__(self):
    return self.to_json()

  def set_value(self, name:str,value):
    self.__dict__[name] = value

  def get_path_to_storage(self):
    if os.path.isabs(self.path_to_storage) and os.path.isdir(self.path_to_storage):
      return self.path_to_storage
    else:
      return os.getcwd()

  def get_value(self, name:str):
    if name in self.__dict__:
      return self.__dict__[name]
    return None

  def get_bot_list_name(self):
    if self.bot_list_name == "":
      return BOT_LIST_FALLBACK
    return self.bot_list_name

  @staticmethod
  def default():
    return Config(
      reddit_app_info={'client_id':'','client_secret':'','user_agent':''},
      subreddits_to_crawl=[],
      number_of_posts=10,
      submission_getter={GETTER_TYPE:SubmissionGetters.HOT.value},
      verbose=True,
      repeat_hours= 0,
      repeat_minutes= 0,
      repeat_seconds= 0,
      batch_save_interval_seconds= 350,
      stream_save_interval_seconds= 300,
      to_date="YYYY-MM-DD",
      from_date="YYYY-MM-DD",
      path_to_storage="",
      bot_list_name="bot_list.json")

  @staticmethod
  def load(filename: str):
    if not path.exists(filename):
      raise NoConfigExists(filename)
    else:
      with open(filename, 'r') as f:
        content = f.read()
        config = Config.default()
        config.__dict__.update(jsonpickle.decode(content))
        return config