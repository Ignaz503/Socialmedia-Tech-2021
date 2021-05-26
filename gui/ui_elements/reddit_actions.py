
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

from reddit_crawl.util.diagnostics import Reddit_Crawl_Diagnostics
from gui.ui_elements.windows.diagnostics_window import DiagnosticsWindow,StreamObservationDiagnosticsWindow

class RedditActions(UIElement):
  __active_crawl_btn: DelayedToggleButton
  __stream_observation_button: DelayedToggleButton
  __historic_crawl_button: DelayedToggleButton

  __active_crawl_cancel_token: Cancel_Token
  __stream_observation_cancel_token: Cancel_Token
  __historic_crawl_cancel_token: Cancel_Token

  __active_crawl_diagnostics: Reddit_Crawl_Diagnostics
  __historic_crawl_diagnostics: Reddit_Crawl_Diagnostics
  __stream_observation_diagnostics_submission: Reddit_Crawl_Diagnostics
  __stream_observation_diagnostics_comments: Reddit_Crawl_Diagnostics

  def __init__(self,*args,**kwargs) -> None:
    self.__active_crawl_btn = None
    self.__stream_observation_button = None
    self.__historic_crawl_button = None
    self.__active_crawl_cancel_token = Cancel_Token()
    self.__stream_observation_cancel_token = Cancel_Token()
    self.__historic_crawl_cancel_token = Cancel_Token()
    self.__active_crawl_diagnostics = Reddit_Crawl_Diagnostics()
    self.__historic_crawl_diagnostics = Reddit_Crawl_Diagnostics()
    self.__stream_observation_diagnostics_submission = Reddit_Crawl_Diagnostics()
    self.__stream_observation_diagnostics_comments = Reddit_Crawl_Diagnostics()
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

  def start_diagnostics_windows(self,master):

    x_pos = int(self.winfo_screenwidth()/2)
    y_pos = int(self.winfo_screenheight()/2)

    DiagnosticsWindow(self.__active_crawl_diagnostics,
      "Active Crawl Diagnostics",
      master = master)
    DiagnosticsWindow(self.__historic_crawl_diagnostics,
      "Historic Crawl Diagnostics",
      master = master)

    StreamObservationDiagnosticsWindow(self.__stream_observation_diagnostics_comments,
      self.__stream_observation_diagnostics_submission,
      "Stream Observation Diagnostics",
      master = master)

  def __run_active_crawl(self):
    self.__active_crawl_cancel_token = Cancel_Token()
    self.__active_crawl_diagnostics.reset()
    self.__active_crawl_btn.change_wait_on_object(self.__active_crawl_cancel_token)
    active_crawl.run(
      config= self.application.config,
      logger=self.application.get_logger(),
      blacklist=self.application.get_bot_list(),
      batch_queue=self.application.get_batch_queue(),
      token=self.__active_crawl_cancel_token,
      diagnostics=self.__active_crawl_diagnostics)

  def __run_stream_observation(self):
    self.__stream_observation_cancel_token = Cancel_Token()
    self.__stream_observation_diagnostics_submission.reset()
    self.__stream_observation_diagnostics_comments.reset()
    self.__stream_observation_button.change_wait_on_object(self.__stream_observation_cancel_token)
    stream_observation.run(
      config = self.application.config,
      logger= self.application.get_logger(),
      blacklist=self.application.get_bot_list(),
      queue=self.application.get_batch_queue(),
      token = self.__stream_observation_cancel_token,
      diagnostics_comments=self.__stream_observation_diagnostics_comments,
      diagnostics_submissions= self.__stream_observation_diagnostics_submission)

  def __run_historic_crawl(self):
    self.__historic_crawl_cancel_token = Cancel_Token()
    self.__historic_crawl_diagnostics.reset()
    self.__historic_crawl_button.change_wait_on_object(self.__historic_crawl_cancel_token)
    historic_crawl.run(
      config=self.application.config,
      logger=self.application.get_logger(),
      blacklist=self.application.get_bot_list(),
      batch_queue=self.application.get_batch_queue(),
      token=self.__historic_crawl_cancel_token,
      callback=self.__historic_crawl_callback,
      diagnostics=self.__historic_crawl_diagnostics
    )

  def __historic_crawl_callback(self):
    if self.__historic_crawl_button.get_state():
      self.__historic_crawl_button.switch() #switch of

  def any_action_running(self)->bool:
    return self.__active_crawl_btn.get_state() or self.__historic_crawl_button.get_state() or self.__stream_observation_button.get_state()

  def stop_any_running_action(self):
    if self.__active_crawl_btn.get_state():
      self.__active_crawl_btn.switch()
    if self.__stream_observation_button.get_state():
      self.__stream_observation_button.switch()
    if self.__historic_crawl_button.get_state():
      self.__historic_crawl_button.switch()
