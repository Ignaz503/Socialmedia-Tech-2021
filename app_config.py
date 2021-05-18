import jsonpickle
from os import path
from submission_getters import HotSubmissionGetter, NewSubmissionGetter, SubmissionsGetter

FILE = "app.config"

class Config:
  subreddits_to_crawl: list[str]
  number_of_posts: int
  submission_getter:SubmissionsGetter
  verbose: bool
  repeat_seconds:int
  repeat_minutes:int
  repeat_hours:int
  max_repetitions:int

  def __init__(self,subreddits_to_crawl: list[str],number_of_posts: int,submission_getter:SubmissionsGetter, verbose: bool,repeat_seconds:int,repeat_minutes:int,repeat_hours:int, max_repetitions:int) -> None:
      self.subreddits_to_crawl = subreddits_to_crawl
      self.number_of_posts = number_of_posts
      self.submission_getter = submission_getter
      self.verbose = verbose
      self.repeat_hours = repeat_hours
      self.repeat_minutes = repeat_minutes
      self.repeat_seconds = repeat_seconds
      self.max_repetitions = max_repetitions
  
  def get_repeat_time_in_seconds(self):
    return self.repeat_seconds + (self.repeat_minutes*60) + (self.repeat_hours * 60 * 60)

  def to_json(self):
    return jsonpickle.encode(self, indent=2)

def load(file_path: str) -> Config:
  if not path.exists(file_path):
    return Config([],10,NewSubmissionGetter())
  else:
    with open(file_path, 'r') as f:
      content = f.read()
      return jsonpickle.decode(content)