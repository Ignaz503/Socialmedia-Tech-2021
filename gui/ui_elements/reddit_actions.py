
from tkinter.constants import LEFT, RIGHT, TRUE
from utility.simple_logging import Level
from tkinter import NS,X
from gui.ui_elements.ui_element import UIElement
from gui.ui_elements.toggle_button import DelayedToggleButton

from utility.cancel_token import Cancel_Token
from gui.ui_elements.toggle_button import WaitOptions

import reddit_crawl.active_crawl as active_crawl
import reddit_crawl.stream_observation as stream_observation
import reddit_crawl.historical_crawl as historic_crawl



class RedditActions(UIElement):
  __active_crawl_btn: DelayedToggleButton
  __stream_observation_button: DelayedToggleButton
  __historic_crawl_button: DelayedToggleButton

  __active_crawl_cancel_token: Cancel_Token
  __stream_observation_cancel_token: Cancel_Token
  __historic_crawl_cancel_token: Cancel_Token

  def __init__(self,*args,**kwargs) -> None:
    self.__active_crawl_btn = None
    self.__stream_observation_button = None
    self.__historic_crawl_button = None
    self.__active_crawl_cancel_token = Cancel_Token()
    self.__stream_observation_cancel_token = Cancel_Token()
    self.__historic_crawl_cancel_token = Cancel_Token()
    super().__init__(*args,**kwargs)
  
  def _build(self) -> None :

    self.__active_crawl_btn =DelayedToggleButton(
      wait_when=WaitOptions.TRUE_TO_FALSE,
      wait_on= self.__active_crawl_cancel_token,
      before_wait_action= lambda: self.__active_crawl_cancel_token.request_cancel(),
      wait_message="waiting on crawl to stop",
      logger=self.application.get_logger(),
      on_true= self.__run_active_crawl,
      on_false= lambda: None,
      when_true="stop active reddit crawl",
      when_false="start active reddit crawl",
      master=self)  
    self.__active_crawl_btn.pack(side=LEFT,fill=X, padx=5, expand=TRUE)

    self.__historic_crawl_button = DelayedToggleButton(
      wait_when= WaitOptions.TRUE_TO_FALSE,
      wait_on= self.__historic_crawl_cancel_token,
      before_wait_action = lambda: self.__historic_crawl_cancel_token.request_cancel(),
      wait_message="waiting on historic crawl to stop",
      logger=self.application.get_logger(),
      on_true=self.__run_historic_crawl,
      on_false=lambda: None,
      when_true="stop historic reddit crawl",
      when_false="start historic reddit crawl",
      master=self)
    self.__historic_crawl_button.pack(side= LEFT,fill=X, padx=5,expand=TRUE)

    self.__stream_observation_button = DelayedToggleButton(
      wait_when=WaitOptions.TRUE_TO_FALSE,
      wait_on= self.__stream_observation_cancel_token,
      before_wait_action = lambda: self.__stream_observation_cancel_token.request_cancel(),
      wait_message="waiting on stream observation to stop",
      logger= self.application.get_logger(),
      on_true= self.__run_stream_observation,
      on_false=lambda: None,
      when_true="stop stream reddit observation",
      when_false="start stream reddit observation",
      master=self)   
    self.__stream_observation_button.pack(side=RIGHT,fill=X, padx=5,expand=TRUE)

  def __run_active_crawl(self):
    self.__active_crawl_cancel_token = Cancel_Token()
    self.__active_crawl_btn.change_wait_on_object(self.__active_crawl_cancel_token)
    active_crawl.run(
      config= self.application.config,
      logger=self.application.get_logger(),
      blacklist=self.application.get_bot_list(),
      batch_queue=self.application.get_batch_queue(),
      token=self.__active_crawl_cancel_token)

  def __run_stream_observation(self):
    self.__stream_observation_cancel_token = Cancel_Token()
    self.__stream_observation_button.change_wait_on_object(self.__stream_observation_cancel_token)
    stream_observation.run(
      config = self.application.config,
      logger= self.application.get_logger(),
      blacklist=self.application.get_bot_list(),
      queue=self.application.get_batch_queue(),
      token = self.__stream_observation_cancel_token)

  def __run_historic_crawl(self):
    self.__historic_crawl_cancel_token = Cancel_Token()
    self.__historic_crawl_button.change_wait_on_object(self.__historic_crawl_cancel_token)
    historic_crawl.run(
      config=self.application.config,
      logger=self.application.get_logger(),
      blacklist=self.application.get_bot_list(),
      batch_queue=self.application.get_batch_queue(),
      token=self.__historic_crawl_cancel_token
    )

  def any_action_running(self)->bool:
    return self.__active_crawl_btn.get_state() or self.__historic_crawl_button.get_state() or self.__stream_observation_button.get_state()