from reddit_crawl.util.submission_getters import SubmissionGetters
import jsonpickle
from utility.app_config import Config
from utility.simple_logging import Level
import datetime as dt
import gui.app_gui as appGUI
from defines import CONFIG

class RedditCrawlApplication:
  __gui: appGUI.RedditCrawlGUI
  config: Config
  def __init__(self, config: Config) -> None:
    self.config = config
    self.__gui = appGUI.RedditCrawlGUI(self)
  
  def run(self):
    self.__gui.run()

  def get_subbredits_to_crawl(self) -> list[str]:
    list = self.__gui.get_subbredtis_to_crawl().split("\n")
    while '' in list: 
      list.remove('')
    return list

  def get_secrets_for_crawl(self)-> dict[str,str]:
    return self.__gui.get_secrets_for_crawl()

  def log(self,message: str, lvl: Level = Level.INFO):
    if not message.endswith("\n"):
      message+="\n"
    time = "[{d}][{ms}] ".format(d = dt.datetime.now().isoformat(sep=" "), ms=lvl.value)
    self.__gui.display_log_message(time + message)

app = RedditCrawlApplication(Config.load(CONFIG))
app.run()