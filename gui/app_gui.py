from tkinter import Frame, Tk
from tkinter.constants import NS, NSEW, W
from utility.app_config import Config
from gui.ui_elements.log_display import Logging_Frame
from gui.ui_elements.subbreddits_to_crawl_gui import Subbredits_To_Crawl_GUI
from gui.ui_elements.reddit_secrets import Reddit_Crawl_Secrets
import gui.ui_elements.reddit_actions as ract

class RedditCrawlGUI:
  __main_window: Tk
  __log_disiplay: Logging_Frame
  __subreddits_to_crawl_input: Subbredits_To_Crawl_GUI
  __reddit_secrets: Reddit_Crawl_Secrets
  def __init__(self, application) -> None:
    self.__main_window = Tk()
    self.__main_window.title("TEAM 1 REDDIT CRAWL")
    self.__log_disiplay = None
    self.__application = application
    self.__main_window.columnconfigure(0, weight=1)
    self.__main_window.rowconfigure(0, weight=1)
    self.__build()

  def __build(self):

    self.__subreddits_to_crawl_input = Subbredits_To_Crawl_GUI(application=self.__application,master= self.__main_window, height=200, pady=5)
    self.__subreddits_to_crawl_input.grid(row=0,column=0,sticky=W+NS)

    self.__reddit_secrets = Reddit_Crawl_Secrets(application=self.__application,master=self.__main_window, pady=5)
    self.__reddit_secrets.grid(row=0,column=1)

    act = ract.RedditActions(application=self.__application,master=self.__main_window)
    act.grid(row=1,column=0,columnspan=2)

    self.__log_disiplay = Logging_Frame(application=self.__application, master = self.__main_window)
    self.__log_disiplay.grid(row = 2, column=0,columnspan=2)

  def run(self):
    self.__main_window.mainloop()
  
  def display_log_message(self, message: str):
    self.__log_disiplay.display(message)
  
  def get_subbredtis_to_crawl(self):
    return self.__subreddits_to_crawl_input.get_subbredits()

  def get_secrets_for_crawl(self)-> dict[str,str]:
    return { "id":self.__reddit_secrets.get_client_id(),
      "secret":self.__reddit_secrets.get_client_secret(),
      "user_agent":self.__reddit_secrets.get_user_agent()}



  


