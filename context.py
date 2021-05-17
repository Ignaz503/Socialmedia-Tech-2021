from bot_blacklist import Bot_Blacklist
from simple_logging import Logger
import praw.models
from praw.reddit import Reddit
from app_config import Config
from subreddit import Subreddit_Data

class Context:
  reddit: Reddit
  config: Config
  current_data: Subreddit_Data
  logger: Logger
  blacklist: Bot_Blacklist

  def __init__(self, reddit: Reddit,config: Config, current_data: Subreddit_Data, logger: Logger, blacklist: Bot_Blacklist) -> None:
      self.reddit = reddit
      self.config = config 
      self.current_data = current_data
      self.logger = logger
      self.blacklist = blacklist