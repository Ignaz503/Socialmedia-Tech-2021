import jsonpickle
from os import path
import datetime as dt
from submission_getters import SubmissionsGetter

class NoConfigExists(Exception):
  def __init__(self,name:str,  *args: object) -> None:
      super().__init__("No app config file with {n} exists".format(n=name), *args)

class Config:
  subreddits_to_crawl: list[str]
  number_of_posts: int
  submission_getter:SubmissionsGetter
  verbose: bool
  repeat_seconds:int
  repeat_minutes:int
  repeat_hours:int
  batch_save_interval_seconds:int
  stream_save_interval_seconds:int
  from_date: str
  to_data: str
  visualization_name:str
  bot_list_name:str
  meta_data_name:str
  def __init__(self,  subreddits_to_crawl: list[str],
                      number_of_posts: int,submission_getter:SubmissionsGetter,
                      verbose: bool,
                      repeat_seconds:int,
                      repeat_minutes:int,
                      repeat_hours:int,
                      batch_save_interval_seconds:int,
                      stream_save_interval_seconds:int,
                      from_date: str,
                      to_data: str,
                      visualization_name:str,
                      bot_list_name:str,
                      meta_data_name:str) -> None:
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
      self.to_data = to_data
      self.visualization_name = visualization_name
      self.bot_list_name = bot_list_name
      self.meta_data_name = meta_data_name
  
  def get_repeat_time_in_seconds(self):
    return self.repeat_seconds + (self.repeat_minutes*60) + (self.repeat_hours * 60 * 60)

  def start_epoch(self)-> int:
    from_d = dt.date.fromisoformat(self.from_date)
    from_dt = dt.datetime(from_d.year,from_d.month,from_d.day,0,0,0)
    return int(from_dt.timestamp())

  def end_epoch(self):
    to_d = dt.date.fromisoformat(self.from_date)
    to_dt = dt.datetime(to_d.year,to_d.month,to_d.day,23,59,59)
    return int(to_dt.timestamp())

  def to_json(self):
    return jsonpickle.encode(self, indent=2)

def load(filename: str) -> Config:
  if not path.exists(filename):
    raise NoConfigExists(filename)
  else:
    with open(filename, 'r') as f:
      content = f.read()
      return jsonpickle.decode(content)