import threading
from typing import Callable
import reddit_crawl.data.bot_blacklist as bot_list
from reddit_crawl.data.bot_blacklist import Threadsafe_Bot_Blacklist
from utility.cancel_token import Thread_Owned_Token_Tray
from utility.app_config import Config
from utility.simple_logging import LOG_TEXT, Level, Sperate_Process_Logger
import datetime as dt
import gui.app_gui as appGUI
from defines import CONFIG
from tkinter.messagebox import showwarning
import utility.simple_logging as simple_logging
from utility.simple_logging import Logger
import utility.data_util as data_util
import reddit_crawl.util.subreddit_batch_queue_data_saver as data_saver
from reddit_crawl.data.subreddit import Subreddit_Batch_Queue
from utility.event import Event
import time

class RedditCrawlApplication:
  __gui: appGUI.RedditCrawlGUI
  config: Config
  __data_saver_token_tray: Thread_Owned_Token_Tray
  __logger: Sperate_Process_Logger
  __batch_queue: Subreddit_Batch_Queue
  __bot_list: Threadsafe_Bot_Blacklist
  __config_update_event:Event
  def __init__(self, config: Config) -> None:
    self.config = config
    self.__config_update_event = Event(value_name=str)
    data_util.ensure_data_locations(config)
    self.__logger = simple_logging.start(config)
    self.__config_update_event.register(self.__handle_storage_path_update)
    self.__gui = appGUI.RedditCrawlGUI(self)
    self.__data_saver_token_tray = Thread_Owned_Token_Tray()
    self.__batch_queue = Subreddit_Batch_Queue()
    self.__bot_list = bot_list.load(config.get_bot_list_name(),config)
    data_saver.run(self.config,self.__logger,self.__batch_queue,self.__data_saver_token_tray)

  def run(self):
    self.__gui.run()

  def get_subbredits_to_crawl(self) -> list[str]:
    return self.__gui.get_subbredtis_to_crawl()

  def get_secrets_for_crawl(self)-> dict[str,str]:
    return self.__gui.get_secrets_for_crawl()

  def update_config_secrets(self):
    self.config.reddit_app_info.update(self.get_secrets_for_crawl())
    self.__config_update_event(value_name="reddit_app_info")

  def set_config_value(self, name:str, value):
    self.config.set_value(name,value)
    self.__config_update_event(value_name=name)

  def register_to_config_update(self,func: Callable[[str],None]):
    self.__config_update_event.register(func)

  def get_batch_queue(self):
    return self.__batch_queue

  def get_logger(self) -> Logger:
    return self.__logger

  def get_bot_list(self):
    return self.__bot_list

  def log(self,message: str, lvl: Level = Level.INFO):
    self.__logger.log(message,lvl)

  def update_subs_to_crawl(self,subs: list[str]):
    old_subs = self.config.subreddits_to_crawl
    self.config.set_value("subreddits_to_crawl",subs)
    if len(old_subs) != len(self.config.subreddits_to_crawl):
      self.__config_update_event(value_name="subreddits_to_crawl")
    elif not all([sub in old_subs for sub in self.config.subreddits_to_crawl]):
      self.__config_update_event(value_name="subreddits_to_crawl")

  def close(self):
    self.log("Staring closing procedure")
    thread = threading.Thread(name="closing procedure",target=self.__handle_shutdown)
    thread.start()

  def __handle_storage_path_update(self,value_name):
    if value_name == "path_to_storage":
      self.__logger.log("updaing storage path")
      self.__logger.update_log_storage_path(self.config.get_path_to_storage())
      data_util.ensure_data_locations(self.config)

  def __handle_shutdown(self):
    self.__gui.stop_any_running_action()
    while self.__gui.any_action_running():
      time.sleep(1)
    self.__data_saver_token_tray.try_rqeuest_cancel()
    self.__data_saver_token_tray.try_wait()
    self.__bot_list.save_to_file(self.config.get_bot_list_name(),self.config)
    self.__logger.stop()
    self.__gui.quit()

if __name__ == '__main__':
  app = RedditCrawlApplication(Config.load(CONFIG))
  app.run()