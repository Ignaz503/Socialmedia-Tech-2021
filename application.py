import reddit_crawl.data.bot_blacklist as bot_list
from reddit_crawl.data.bot_blacklist import Threadsafe_Bot_Blacklist
from utility.cancel_token import Thread_Owned_Token_Tray
from utility.app_config import Config
from utility.simple_logging import LOG_TEXT, Level
import datetime as dt
import gui.app_gui as appGUI
from defines import CONFIG
from tkinter.messagebox import showwarning
import utility.simple_logging as simple_logging
from utility.simple_logging import Logger
import reddit_crawl.util.subreddit_batch_queue_data_saver as data_saver
from reddit_crawl.data.subreddit import Subreddit_Batch_Queue

class RedditCrawlApplication:
  __gui: appGUI.RedditCrawlGUI
  config: Config
  __data_saver_token_tray: Thread_Owned_Token_Tray
  __logger: Logger
  __batch_queue: Subreddit_Batch_Queue
  __bot_list: Threadsafe_Bot_Blacklist
  def __init__(self, config: Config) -> None:
    self.config = config
    self.__logger = simple_logging.start(config.verbose)
    self.__gui = appGUI.RedditCrawlGUI(self)
    self.__data_saver_token_tray = Thread_Owned_Token_Tray()
    self.__batch_queue = Subreddit_Batch_Queue()
    self.__bot_list = bot_list.load(config.bot_list_name)
    data_saver.run(self.config,self.__logger,self.__batch_queue,self.__data_saver_token_tray)

  def run(self):
    self.__gui.run()

  def get_subbredits_to_crawl(self) -> list[str]:
    return self.__gui.get_subbredtis_to_crawl()

  def get_secrets_for_crawl(self)-> dict[str,str]:
    return self.__gui.get_secrets_for_crawl()

  def update_config(self):
    self.config.reddit_app_info.update(self.get_secrets_for_crawl())

  def set_config_value(self, name:str, value):
    self.config.set_value(name,value)

  def get_batch_queue(self):
    return self.__batch_queue

  def get_logger(self) -> Logger:
    return self.__logger

  def get_bot_list(self):
    return self.__bot_list

  def log(self,message: str, lvl: Level = Level.INFO):
    self.__logger.log(message,lvl)


  def close(self,):
    if self.__gui.any_action_running():
      showwarning("Reddit","There are still actions running, stop them for a gracefull exit")
      return
    self.__data_saver_token_tray.try_rqeuest_cancel()
    self.__data_saver_token_tray.try_wait()
    self.__logger.stop()
    self.__gui.quit()

if __name__ == '__main__':
  app = RedditCrawlApplication(Config.load(CONFIG))
  app.run()