from tkinter import Frame, Tk
from tkinter.constants import BOTTOM, NS, NSEW, TOP, W, X
from gui.ui_elements.subbreddits_to_crawl_gui import Subbredits_To_Crawl_GUI
from gui.ui_elements.reddit_secrets import Reddit_Crawl_Secrets
import gui.ui_elements.reddit_actions as ract
from gui.ui_elements.menu_bar import MenuBar
from gui.ui_elements.generator_actions import GeneratorActions

class RedditCrawlGUI:
  __main_window: Tk
  __subreddits_to_crawl_input: Subbredits_To_Crawl_GUI
  __reddit_secrets: Reddit_Crawl_Secrets
  __reddit_actions: ract.RedditActions
  __processing_actions: GeneratorActions
  def __init__(self, application) -> None:
    self.__main_window = Tk()
    self.__main_window.title("TEAM 1 REDDIT CRAWL")
    self.__reddit_actions = None
    self.__reddit_secrets = None
    self.__subreddits_to_crawl_input = None
    self.__processing_actions = None
    self.__application = application
    self.__main_window.columnconfigure(0, weight=1)
    self.__main_window.rowconfigure(0, weight=1)
    self.__main_window.protocol("WM_DELETE_WINDOW",self.__application.close)
    self.__build()

  def __build(self):
    self.__subreddits_to_crawl_input = Subbredits_To_Crawl_GUI(application=self.__application,master= self.__main_window, height=200, pady=5)
    self.__subreddits_to_crawl_input.grid(row=0,column=0,sticky=W+NS)

    self.__reddit_secrets = Reddit_Crawl_Secrets(application=self.__application,master=self.__main_window, pady=5)
    self.__reddit_secrets.grid(row=0,column=1)

    action_frame = Frame(self.__main_window)
    action_frame.grid(row=1,column=0,columnspan=2)
    self.__reddit_actions = ract.RedditActions(application=self.__application,master=action_frame)
    self.__reddit_actions.pack(fill=X, side=TOP, pady=5,padx=5,expand=True)

    self.__processing_actions = GeneratorActions(application=self.__application,master=action_frame)
    self.__processing_actions.pack(fill=X, side=BOTTOM, pady=5,padx=5,expand=True)

    menubar = MenuBar(application=self.__application,master=self.__main_window)
    self.__main_window.configure(menu=menubar)

  def run(self):
    self.__main_window.mainloop()
  
  def get_subbredtis_to_crawl(self):
    return self.__subreddits_to_crawl_input.get_subbredits()

  def get_secrets_for_crawl(self)-> dict[str,str]:
    return { "id":self.__reddit_secrets.get_client_id(),
      "secret":self.__reddit_secrets.get_client_secret(),
      "user_agent":self.__reddit_secrets.get_user_agent()}

  def any_action_running(self)->bool:
    return self.__reddit_actions.any_action_running() or self.__processing_actions.any_action_running()

  def stop_any_running_action(self):
    self.__reddit_actions.stop_any_running_action()
    self.__processing_actions.stop_any_running_action()

  def quit(self):
    self.__main_window.quit()

  


