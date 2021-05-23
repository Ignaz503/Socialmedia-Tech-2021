import time
from tkinter.constants import LEFT, RIGHT, TRUE
from utility.simple_logging import Level
from tkinter import NS,X
from gui.ui_elements.ui_element import UIElement
from gui.ui_elements.toggle_button import DelayedToggleButton

from utility.waitableobject import Waitable_Object
from gui.ui_elements.toggle_button import WaitOptions

class FakeWait(Waitable_Object):
  def __init__(self,app) -> None:
      super().__init__()
      self.app = app
  
  def wait(self):
    self.app.log("before sleep")
    time.sleep(10)
    self.app.log("after sleep")


class RedditActions(UIElement):
  def __init__(self,*args,**kwargs) -> None:
    super().__init__(*args,**kwargs)
  
  def __test(self,te: str):
    self.application.log(te, Level.INFO)

  def _build(self) -> None:

    btn =DelayedToggleButton(
      wait_when=WaitOptions.TRUE_TO_FALSE,
      wait_on= FakeWait(self.application),
      wait_message="waiting on crawl to stop",
      on_true= lambda:self.__test("active start"),
      on_false= lambda: self.__test("active stop"),
      when_true="stop active reddit crawl",
      when_false="start active reddit crawl",
      master=self)  
    btn.pack(side=LEFT,fill=X, padx=5, expand=TRUE)

    btn = DelayedToggleButton(
      wait_when= WaitOptions.TRUE_TO_FALSE,
      wait_on= FakeWait(self.application),
      wait_message="waiting on historic crawl to stop",
      on_true=lambda:self.__test("historic start"),
      on_false=lambda: self.__test("historic stop"),
      when_true="stop historic reddit crawl",
      when_false="start historic reddit crawl",
      master=self)
    btn.pack(side= LEFT,fill=X, padx=5,expand=TRUE)

    btn = DelayedToggleButton(
      wait_when=WaitOptions.TRUE_TO_FALSE,
      wait_on= FakeWait(self.application),
      wait_message="waiting on stream observation to stop",
      on_true=lambda:self.__test("stream start"),
      on_false=lambda: self.__test("stream stop"),
      when_true="stop stream reddit observation",
      when_false="start stream reddit observation",
      master=self)   
    btn.pack(side=RIGHT,fill=X, padx=5,expand=TRUE)