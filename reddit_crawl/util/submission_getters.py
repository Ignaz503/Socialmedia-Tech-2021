from logging import Logger
from utility.simple_logging import Level
from enum import Enum
from defines import GETTER_TYPE, GETTER_CATEGORY

class SubmissionGetters(Enum):
  HOT = 'hot'
  TOP = 'top'
  NEW = 'new'
  RISING = 'rising'

class TopCategories(Enum):
  ALL ='all'
  DAY = 'day'
  HOUR = 'hour'
  MONTH = 'month'
  WEEK = 'week'
  YEAR = 'year'

class SubmissionsGetter:
  def __init__(self) -> None:
      pass
  def get(self, subreddit, number_of_posts: int, logger: Logger):
    pass

class TopSubmissionGetter(SubmissionsGetter):
  category: str
  def __init__(self, top_category: str) -> None:
      super().__init__()
      self.category = top_category

  def get(self, subreddit,  number_of_posts: int, logger: Logger):
    logger.log("Getting {number} top posts from category {cat}".format(number= number_of_posts, cat=self.category),Level.INFO)
    return subreddit.top(self.category,limit= number_of_posts)

class HotSubmissionGetter(SubmissionsGetter):
  def __init__(self) -> None:
      super().__init__()
  
  def get(self, subreddit, number_of_posts: int, logger: Logger):
      logger.log("Getting {number} hot posts".format(number = number_of_posts),Level.INFO)
      return subreddit.hot(limit= number_of_posts)

class NewSubmissionGetter(SubmissionsGetter):
  def __init__(self) -> None:
      super().__init__()

  def get(self, subreddit, number_of_posts:int, logger: Logger):
    logger.log( "Getting {number} of new posts".format(number = number_of_posts),Level.INFO)
    return subreddit.new(limit= number_of_posts)

class RisingSubmissionGetter(SubmissionsGetter):
  def __init__(self) -> None:
      super().__init__()

  def get(self, subreddit, number_of_posts: int, logger: Logger):
    logger.log("Getting {number} rising posts".format(number = number_of_posts),Level.INFO)
    return subreddit.rising(limit= number_of_posts)

def create_gettter(data: dict[str,str])->SubmissionsGetter:
  if GETTER_TYPE in data:
    val = data[GETTER_TYPE]
    if val is SubmissionGetters.HOT.value:
      return HotSubmissionGetter()
    if val is SubmissionGetters.NEW.value:
      return NewSubmissionGetter()
    if val is SubmissionGetters.RISING.value:
      return RisingSubmissionGetter()
    if val is SubmissionGetters.TOP.value:
      cat = "all"
      if GETTER_CATEGORY in data:
        cat = data[GETTER_CATEGORY]
      return TopSubmissionGetter(cat)
  return HotSubmissionGetter()