from logging import Logger
from praw import Reddit
from praw.models import Subreddit
from enum import Enum

class SubmissionsGetter:
  def __init__(self) -> None:
      pass
  def get(self, subreddit: Subreddit, number_of_posts: int, logger: Logger):
    pass


class TopSubmissionGetter(SubmissionsGetter):
  category: str
  def __init__(self, top_category: str) -> None:
      super().__init__()
      self.category = top_category

  def get(self, subreddit: Subreddit,  number_of_posts: int, logger: Logger):
    logger.log("Getting {number} top posts from category {cat} from subreddit {sub}".format(number= number_of_posts, cat=self.category,sub=subreddit.display_name))
    return subreddit.top(self.category,limit= number_of_posts)

class HotSubmissionGetter(SubmissionsGetter):
  def __init__(self) -> None:
      super().__init__()
  
  def get(self, subreddit: Subreddit, number_of_posts: int, logger: Logger):
      logger.log("Getting {number} hot posts from subreddit {sub}".format(number = number_of_posts,sub=subreddit.display_name))
      return subreddit.hot(limit= number_of_posts)

class NewSubmissionGetter(SubmissionsGetter):
  def __init__(self) -> None:
      super().__init__()

  def get(self, subreddit: Subreddit, number_of_posts:int, logger: Logger):
    logger.log( "Getting {number} of new posts from subreddit {sub}".format(number = number_of_posts,sub=subreddit.display_name))
    return subreddit.new(limit= number_of_posts)

class RisingSubmissionGetter(SubmissionsGetter):
  def __init__(self) -> None:
      super().__init__()

  def get(self, subreddit: Subreddit, number_of_posts: int, logger: Logger):
    logger.log("Getting {number} rising posts from subreddit {sub}".format(number = number_of_posts,sub=subreddit.display_name))
    return subreddit.rising(limit= number_of_posts)

