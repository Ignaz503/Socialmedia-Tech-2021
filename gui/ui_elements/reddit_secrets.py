import tkinter
from gui.ui_elements.toggle_button import Toggle_Button, DelayedToggleButton
from tkinter import Button, Frame,Label, Entry
from tkinter.constants import BOTH, BOTTOM, LEFT, N, END, RIGHT, TOP,X
import tkinter.filedialog as tkfd
from io import TextIOWrapper
import jsonpickle
from gui.ui_elements.ui_element import UIElement
from defines import CLIENT_ID, CLIENT_SECRET, USER_AGENT
from utility.app_config import Config
import tkinter.messagebox as messagebox


class Reddit_Crawl_Secrets(UIElement): 
  def __init__(self,*args, **kwargs) -> None:
    self.__client_id_input = None
    self.__client_secret_input = None
    self.__client_user_agent_input = None
    super().__init__(*args,**kwargs)

  def _build(self) -> None:
    client_id_frame = Frame(master=self,width=200)
    client_id_frame.pack(fill=X,padx=5, side=TOP)

    id_label = Label(client_id_frame, text="Client ID:")
    id_label.pack(side=LEFT, padx=5, pady=5)

    self.__client_id_input = Entry(client_id_frame,validate="focusout", validatecommand=lambda: self.__update_config_id_entry())
    self.__client_id_input.pack(fill=X, padx=5, expand=True)

    client_secret_frame = Frame(master=self)
    client_secret_frame.pack(fill=X,padx=5)

    secret_label = Label(client_secret_frame, text="Client Secret:")
    secret_label.grid(row=0,column=0)

    self.__client_secret_input = Entry(client_secret_frame,show="*",validate="focusout", validatecommand=lambda: self.__update_config_secret_entry())
    self.__client_secret_input.grid(row=0,column=1)

    btn = Toggle_Button(
      on_true=lambda:self.__client_secret_input.configure(show=""),
      on_false=lambda: self.__client_secret_input.configure(show="*"),
      when_false= "show",
      when_true="hide",
      master=client_secret_frame
    )
    btn.grid(row=0,column=2)

    user_agent_frame = Frame(master=self)
    user_agent_frame.pack(fill=X,padx=5)

    user_agent_label = Label(user_agent_frame, text="User Agent:")
    user_agent_label.pack(side=LEFT, padx=5, pady=5)

    self.__client_user_agent_input = Entry(user_agent_frame,validate="focusout", validatecommand=lambda: self.__update_config_user_agent_entry())
    self.__client_user_agent_input.pack(fill=X, padx=5, expand=True)

    config: Config = self.application.config
    self.__update_field_from_dict(config.reddit_app_info)

    from_file_frame = Frame(master=self)
    from_file_frame.pack(fill=X,padx=5, side=BOTTOM)

    from_file_btn = Button(master=from_file_frame,text="Load From File",command=lambda: self.load_from_file())
    from_file_btn.pack(fill=X,expand=True)

  def load_from_file(self):
    data: TextIOWrapper = tkfd.askopenfile()
    if data is None:
      return
    with data:
      content = data.read()
      self.__update_field_from_dict(jsonpickle.decode(content))

  def __update_config_entry(self, dict_entry: str, val:str):
    c: Config = self.application.config
    if c.reddit_app_info[dict_entry] != val:
      self.application.update_config_secrets()

  def __update_config_id_entry(self):
    self.__update_config_entry(CLIENT_ID,self.__client_id_input.get())

  def __update_config_secret_entry(self):
    self.__update_config_entry(CLIENT_SECRET,self.__client_secret_input.get())

  def __update_config_user_agent_entry(self):
    self.__update_config_entry(USER_AGENT,self.__client_user_agent_input.get())

  def __update_field_from_dict(self, data: dict[str,str]):
    if CLIENT_ID in data:
      self.__client_id_input.delete(0,END)
      self.__client_id_input.insert(END,data[CLIENT_ID])
    if CLIENT_SECRET in data:
      self.__client_secret_input.delete(0,END)
      self.__client_secret_input.insert(END,data[CLIENT_SECRET])
    if USER_AGENT in data:
      self.__client_user_agent_input.delete(0,END)
      self.__client_user_agent_input.insert(END,data[USER_AGENT])

  def get_client_id(self) -> str:
    return self.__client_id_input.get()
  
  def get_client_secret(self)->str:
    return self.__client_secret_input.get()

  def get_user_agent(self)->str:
    return self.__client_user_agent_input.get()