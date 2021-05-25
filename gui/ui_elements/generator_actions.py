from tkinter.constants import BOTTOM, LEFT, RIGHT, TOP, TRUE
from utility.simple_logging import Level
from tkinter import Button, Frame, Label, NS, OptionMenu, StringVar,X
from gui.ui_elements.ui_element import UIElement
from gui.ui_elements.toggle_button import DelayedToggleButton

from utility.cancel_token import Cancel_Token
from gui.ui_elements.toggle_button import WaitOptions

import generators.data_generator as data_generator
import generators.visualization_generator as visualization_generator
from generators.visualization_generator import VisualizationDataFiles

class GeneratorActions(UIElement):
  __data_generation_btn: DelayedToggleButton
  __visualization_generation_button: DelayedToggleButton

  __data_generation_cancel_token: Cancel_Token
  __visualization_cancel_token: Cancel_Token
  __show_btn_frame:Frame
  __created_vis:bool
  __data_processing_done:bool
  __vis_to_show_var: StringVar

  def __init__(self,*args,**kwargs) -> None:
    self.__data_generation_btn = None
    self.__visualization_generation_button = None
    self.__show_btn_frame= None
    self.__created_vis=False
    self.__data_processing_done=False
    self.__vis_to_show_var = StringVar()
    self.__vis_to_show_var.set(VisualizationDataFiles.SUBREDDIT_SUBREDDIT.name.replace("_","-"))
    self.__data_generation_cancel_token = Cancel_Token()
    self.__visualization_cancel_token = Cancel_Token()
    super().__init__(*args,**kwargs)
    self.application.register_to_config_update(self.__on_config_update)
  
  def _build(self) -> None :

    generator_button_frame = Frame(master=self)
    generator_button_frame.pack(side=TOP,fill=X,padx=5,pady=5, expand=True)

    self.__data_generation_btn =DelayedToggleButton(
      wait_when=WaitOptions.TRUE_TO_FALSE,
      wait_on= self.__data_generation_cancel_token,
      before_wait_action= lambda: self.__data_generation_cancel_token.request_cancel(),
      wait_message="waiting on data processing to stop",
      logger=self.application.get_logger(),
      on_true= self.__run_data_generation,
      on_false= lambda: None,
      when_true="stop data processing",
      when_false="start data processing",
      master=generator_button_frame)  
    self.__data_generation_btn.pack(side=LEFT,fill=X, padx=5, expand=TRUE)

    self.__visualization_generation_button = DelayedToggleButton(
      wait_when=WaitOptions.TRUE_TO_FALSE,
      wait_on= self.__visualization_cancel_token,
      before_wait_action = lambda: self.__visualization_cancel_token.request_cancel(),
      wait_message="waiting on data visualization",
      logger= self.application.get_logger(),
      on_true= self.__run_visualization_generator,
      on_false=lambda: None,
      when_true="stop data visualization",
      when_false="start data viusalization",
      master=generator_button_frame)   
    self.__visualization_generation_button.pack(side=RIGHT,fill=X, padx=5,expand=TRUE)

    self.__show_btn_frame = Frame(master=self)
    self.__pack_show_btn_frame()

    if not self.__created_vis:
      self.__show_btn_frame.pack_forget()

    l = Label(master=self.__show_btn_frame,text="Show Graph:")
    l.grid(row=0,column=0,padx=5)

    show_options = OptionMenu(self.__show_btn_frame,
      self.__vis_to_show_var,
      *[e.name.replace("_","-") for e in VisualizationDataFiles],
      command=lambda var: None)
    show_options.grid(row=0,column=1,padx=5)

    btn = Button(master=self.__show_btn_frame,
        text="Go",
        command=self.__show_visualization)
    btn.grid(row=0,column=2,padx=5)

  def __pack_show_btn_frame(self):
    self.__show_btn_frame.pack(side=BOTTOM,fill=X,pady=5,padx=5,expand=True)

  def __run_data_generation(self):
    self.__data_generation_cancel_token = Cancel_Token()
    self.__data_generation_btn.change_wait_on_object(self.__data_generation_cancel_token)
    data_generator.run(
      config= self.application.config,
      logger=self.application.get_logger(),
      token=self.__data_generation_cancel_token,
      on_done_callback=lambda: self.__update_data_processing_state(value=True))

  def __run_visualization_generator(self):
    self.__visualization_cancel_token = Cancel_Token()
    self.__visualization_generation_button.change_wait_on_object(self.__visualization_cancel_token)
    visualization_generator.run(
      config = self.application.config,
      logger= self.application.get_logger(),
      token = self.__visualization_cancel_token,
      load_data_from_disk=self.__data_processing_done,
      on_done_callback=lambda: self.__update_visualization_state(value=True) )

  def __update_visualization_state(self,value):
    
    #we came from thread and were running  still
    if value and self.__visualization_generation_button.get_state(): 
      #turn of  
      self.__visualization_generation_button.switch() 
    
    #we came from event and were running therefor we need to stop
    if not value and self.__visualization_generation_button.get_state():
      #turn of
      self.__visualization_generation_button.switch()

    #we came from thread and are not running
    if value and not self.__visualization_generation_button.get_state():
      return

    #we came from event or from thread and were running
    self.__created_vis = value
    if  self.__created_vis:
      self.__pack_show_btn_frame()
    else:
      self.application.log("forgetting layout")
      self.__show_btn_frame.pack_forget()

  def __update_data_processing_state(self,value):
    if value and self.__data_generation_btn.get_state():
      #we were invoked by the thread callback turn off
      self.__data_generation_btn.switch()
    if not value and self.__data_generation_btn.get_state():
      #we are running and were invoked by the event turn off
      self.__data_generation_btn.switch()

    #case we came from thread and are not running
    if value and not self.__data_generation_btn.get_state():
      #we don't set the data flag
      return
    #case we were not running and we came from event
    #value is false state is false -> do nothing

    self.__data_processing_done = value

  def any_action_running(self)->bool:
    return self.__data_generation_btn.get_state() or self.__visualization_generation_button.get_state()

  def __show_visualization(self):
    try:
      self.application.log(f"Showing {self.__vis_to_show_var.get()}")
      VisualizationDataFiles.from_name(self.__vis_to_show_var.get().replace("-","_")).show(self.application.config)
    except ValueError:
      self.application.log("Couldn't parse visualization show option", Level.ERROR)
      pass

  def __on_config_update(self,value_name: str):
    if value_name == "subreddits_to_crawl":
      self.application.log("changed subreddits to crawl")
      self.__update_data_processing_state(False)
      self.__update_visualization_state(value=False)

  def stop_any_running_action(self):
    if self.__data_generation_btn.get_state():
      self.__data_generation_btn.switch()
    if self.__visualization_generation_button.get_state():
      self.__visualization_generation_button.switch()