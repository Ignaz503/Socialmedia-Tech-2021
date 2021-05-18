from bot_blacklist import Bot_Blacklist
from simple_logging import Logger
import praw.models
from praw.reddit import Reddit
from app_config import Config
from subreddit import Subreddit_Data
from diagnostics import Subreddit_Crawl_Diagnostic, Reddit_Crawl_Diagnostics

class Context:
  reddit: Reddit
  config: Config
  current_data: Subreddit_Data
  logger: Logger
  blacklist: Bot_Blacklist
  subreddit_diagnostics: Subreddit_Crawl_Diagnostic
  crawl_diagnostics: Reddit_Crawl_Diagnostics

  def __init__(self, reddit: Reddit,config: Config, current_data: Subreddit_Data, logger: Logger, blacklist: Bot_Blacklist, subreddit_diagnostics: Subreddit_Crawl_Diagnostic, crawl_diagnostics: Reddit_Crawl_Diagnostics) -> None:
      self.reddit = reddit
      self.config = config 
      self.current_data = current_data
      self.logger = logger
      self.blacklist = blacklist
      self.subreddit_diagnostics = subreddit_diagnostics
      self.crawl_diagnostics = crawl_diagnostics