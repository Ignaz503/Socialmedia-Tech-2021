import tkinter
from utility.event import EventRegisterArgumentTypeMismatch
from gui.ui_elements.toggle_button import Toggle_Button, DelayedToggleButton
from tkinter import BooleanVar, Button, Checkbutton, Frame,Label, Entry, Misc
from tkinter.constants import BOTH, BOTTOM, DISABLED, LEFT, N, END, NORMAL, RIGHT, TOP,X
import tkinter.filedialog as tkfd
from io import TextIOWrapper
import jsonpickle
from gui.ui_elements.ui_element import UIElement
from defines import CLIENT_ID, CLIENT_SECRET, USER_ACCOUNT_NAME, USER_ACCOUNT_PWD, USER_AGENT, USE_USER_ACCOUNT
from utility.app_config import Config
import tkinter.messagebox as messagebox
from gui.ui_elements.input_box import EnterAcceptInputBox

class Reddit_Crawl_Secrets(UIElement): 
  def __init__(self,*args, **kwargs) -> None:
    self.__client_id_input = None
    self.__client_secret_input = None
    self.__client_user_agent_input = None
    self.__user_account_name_input = None
    self.__user_account_pwd_input = None
    self.__user_info_frame = None
    self.__use_user_account_btn=None
    self.__use_user_accuount_var = BooleanVar()
    self.__use_user_accuount_var.set(False)
    super().__init__(*args,**kwargs)

  def _build(self) -> None:
    client_id_frame = Frame(master=self,width=200)
    client_id_frame.pack(fill=X,padx=5, side=TOP)

    id_label = Label(client_id_frame, text="Client ID:")
    id_label.pack(side=LEFT, padx=5, pady=5)

    self.__client_id_input = EnterAcceptInputBox(
      on_accept=lambda e: self.__advance_focus_target(self.__client_secret_input),
      focus_target=None,
      master=client_id_frame)
    self.__client_id_input.bind('<FocusOut>', lambda e: self.__update_config_id_entry())
    self.__client_id_input.pack(fill=X, padx=5, expand=True)

    client_secret_frame = Frame(master=self)
    client_secret_frame.pack(fill=X,padx=5)

    secret_label = Label(client_secret_frame, text="Client Secret:")
    secret_label.grid(row=0,column=0)

    self.__client_secret_input = EnterAcceptInputBox(
      on_accept= lambda e: self.__advance_focus_target(self.__client_user_agent_input),
      focus_target=None,
      master=client_secret_frame,
      show="*")
    self.__client_secret_input.bind('<FocusOut>', lambda e: self.__update_config_secret_entry())
    self.__client_secret_input.grid(row=0,column=1)

    btn = Toggle_Button(
      on_true=lambda:self.__client_secret_input.configure(show=""),
      on_false=lambda: self.__client_secret_input.configure(show="*"),
      when_false= "show",
      when_true="hide",
      master=client_secret_frame,
      width = 5
    )
    btn.grid(row=0,column=2)

    user_agent_frame = Frame(master=self)
    user_agent_frame.pack(fill=X,padx=5)

    user_agent_label = Label(user_agent_frame, text="User Agent:")
    user_agent_label.pack(side=LEFT, padx=5, pady=5)

    self.__client_user_agent_input = EnterAcceptInputBox(
      on_accept= lambda e: self.__advance_focus_target(self.__user_account_name_input),
      focus_target=None,
      master=user_agent_frame)
    self.__client_user_agent_input.bind('<FocusOut>',lambda e: self.__update_config_user_agent_entry())
    self.__client_user_agent_input.pack(fill=X, padx=5, expand=True)

    user_login_master_frame = Frame(self)
    user_login_master_frame.pack(fill=X,padx=5)
    self.__use_user_account_btn = Checkbutton(master = self,
       text="Use User Account",
       variable=self.__use_user_accuount_var,
       onvalue=True,
       offvalue=False,
       command=self.__update_use_user_account)
    self.__use_user_account_btn.pack(padx=5, fill=X, expand=True)

    self.__user_info_frame = Frame(master = user_login_master_frame)
    self.__user_info_frame.pack(side=BOTTOM,fill=X,expand=True,padx=5)

    l = Label(master=self.__user_info_frame,text="Name:")
    l.grid(row=0,column=0)
    self.__user_account_name_input= EnterAcceptInputBox(
      on_accept= lambda e: self.__advance_focus_target(self.__user_account_pwd_input),
      focus_target=None,
      master = self.__user_info_frame)
    self.__user_account_name_input.bind('<FocusOut>',lambda e:  self.__update_user_name())
    self.__user_account_name_input.grid(row=0,column=1,columnspan=2)

    l=Label(master= self.__user_info_frame,text="Password:")
    l.grid(row=1,column=0)

    self.__user_account_pwd_input = EnterAcceptInputBox(
      on_accept= lambda e: self.__advance_focus_target(self.__client_id_input),
      focus_target=None,
      master = self.__user_info_frame,
      show="*")
    self.__user_account_pwd_input.bind('<FocusOut>', lambda e: self.__update_user_pwd())
    self.__user_account_pwd_input.grid(row=1,column=1)

    btn = Toggle_Button(
      on_true=lambda:self.__user_account_pwd_input.configure(show=""),
      on_false=lambda: self.__user_account_pwd_input.configure(show="*"),
      when_false= "show",
      when_true="hide",
      master=self.__user_info_frame,
      width = 5
    )
    btn.grid(row=1,column=2)

    config: Config = self.application.config
    self.__update_field_from_dict(config.reddit_app_info)
    self.__toggle_user_account_input_fileds()

    from_file_frame = Frame(master=self)
    from_file_frame.pack(fill=X,padx=5, side=BOTTOM)
    from_file_btn = Button(master=from_file_frame,text="Load From File",command=lambda: self.load_from_file())
    from_file_btn.pack(fill=X,expand=True)

  def __advance_focus_target(self,next: Misc):
    next.focus_set()

  def load_from_file(self):
    data: TextIOWrapper = tkfd.askopenfile()
    if data is None:
      return
    with data:
      content = data.read()
      self.__update_field_from_dict(jsonpickle.decode(content))

  def __toggle_user_account_input_fileds(self):
    if self.__use_user_accuount_var.get():
      self.__user_account_name_input.configure(state=NORMAL)
      self.__user_account_pwd_input.configure(state=NORMAL)
    else:
      self.__user_account_name_input.configure(state=DISABLED)
      self.__user_account_pwd_input.configure(state=DISABLED)

  def __update_config_entry(self, dict_entry: str, val:str):
    c: Config = self.application.config
    if c.reddit_app_info[dict_entry] != val:
      self.application.update_config_secrets()

  def __update_use_user_account(self):
    self.__update_config_entry(USE_USER_ACCOUNT,self.__use_user_accuount_var.get())
    self.__toggle_user_account_input_fileds()

  def __update_user_name(self):
    self.__update_config_entry(USER_ACCOUNT_NAME,self.__user_account_name_input.get())

  def __update_user_pwd(self):
    self.__update_config_entry(USER_ACCOUNT_PWD,self.__user_account_pwd_input.get())

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
    if USE_USER_ACCOUNT in data:
      self.__use_user_accuount_var.set(data[USE_USER_ACCOUNT])
    if USER_ACCOUNT_NAME in data:
      self.__user_account_name_input.delete(0,END)
      self.__user_account_name_input.insert(END,data[USER_ACCOUNT_NAME])
    if USER_ACCOUNT_PWD in data:
      self.__user_account_pwd_input.delete(0,END)
      self.__user_account_name_input.insert(END,data[USER_ACCOUNT_PWD])

  def get_client_id(self) -> str:
    return self.__client_id_input.get()
  
  def get_client_secret(self)->str:
    return self.__client_secret_input.get()

  def get_user_agent(self)->str:
    return self.__client_user_agent_input.get()

  def get_use_user_agent(self)-> bool:
    return self.__use_user_accuount_var.get()

  def get_user_account_name(self)->str:
    return self.__user_account_name_input.get()
  
  def get_user_pwd(self)->str:
    return self.__user_account_pwd_input.get()
