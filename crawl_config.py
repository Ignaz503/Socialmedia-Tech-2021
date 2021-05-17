import jsonpickle
from os import path
from submission_getters import HotSubmissionGetter, NewSubmissionGetter, SubmissionsGetter

FILE = "crawl.config"

class Config:
  subreddits_to_crawl: list[str]
  number_of_posts: int
  submission_getter:SubmissionsGetter
  verbose: bool

  def __init__(self,subreddits_to_crawl: list[str],number_of_posts: int,submission_getter:SubmissionsGetter, verbose: bool) -> None:
      self.subreddits_to_crawl = subreddits_to_crawl
      self.number_of_posts = number_of_posts
      self.submission_getter = submission_getter
      self.verbose = verbose
  
  def to_json(self):
    return jsonpickle.encode(self, indent=2)

def load(file_path: str) -> Config:
  if not path.exists(file_path):
    return Config([],10,NewSubmissionGetter())
  else:
    with open(file_path, 'r') as f:
      content = f.read()
      return jsonpickle.decode(content)