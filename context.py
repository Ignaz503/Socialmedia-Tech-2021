from threading import Lock
from app_config import Config
from praw.reddit import Reddit
from simple_logging import Logger
from subreddit import Subreddit_Batch
from diagnostics import Reddit_Crawl_Diagnostics
from bot_blacklist import Bot_Blacklist, Threadsafe_Bot_Blacklist

class Context:
  reddit: Reddit
  config: Config
  current_data: Subreddit_Batch
  logger: Logger
  blacklist: Threadsafe_Bot_Blacklist
  crawl_diagnostics: Reddit_Crawl_Diagnostics

  def __init__(self, reddit: Reddit,config: Config, current_data: Subreddit_Batch, logger: Logger, blacklist: Bot_Blacklist, crawl_diagnostics: Reddit_Crawl_Diagnostics) -> None:
      self.reddit = reddit
      self.config = config 
      self.current_data = current_data
      self.logger = logger
      self.blacklist = blacklist
      self.crawl_diagnostics = crawl_diagnostics

class Thread_Safe_Context(Context):
  current_data_lock: Lock
  def __init__(self, reddit: Reddit, config: Config, current_data: Subreddit_Batch, logger: Logger, blacklist: Bot_Blacklist, crawl_diagnostics: Reddit_Crawl_Diagnostics) -> None:
      super().__init__(reddit, config, current_data, logger, blacklist, crawl_diagnostics)
      self.current_data_lock = Lock()
