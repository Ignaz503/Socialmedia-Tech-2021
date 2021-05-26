from tkinter.font import BOLD, Font
from reddit_crawl.util.diagnostics import Reddit_Crawl_Diagnostics
from tkinter import Frame, Label, StringVar, Toplevel
from tkinter.constants import BOTH, LEFT, RIGHT, TOP, TRUE, X
from utility.diagnostics import Diagnostics

class DiagnosticsWindow(Toplevel):

  __diagnostics: Diagnostics
  __vars: dict[str,StringVar]

  def __init__(self,diagnostics: Diagnostics,title:str,*args,**kwargs) -> None:
      super().__init__(*args,**kwargs)
      self.__diagnostics = diagnostics
      self.__diagnostics.register_to_update(self.__on_update)
      self.__vars = {}
      self.__build(title)

  def __build(self,title:str):
    self.title(title)
    self.protocol("WM_DELETE_WINDOW", self.__ignore)

    lab = Label(master=self,text=title,font=Font(weight=BOLD),relief="groove", borderwidth=1)
    lab.pack(side=TOP,fill=X,pady=5,expand=True)

    for category in self.__diagnostics.categories():
      var = StringVar()
      self.__vars[category] = var
      var.set(self.__diagnostics.get(category,as_string=True))
      frame = Frame(self,relief="groove", borderwidth=1)
      frame.pack(side=TOP,fill=X,pady=5,expand=True)

      l = Label(master=frame,text=f"{category}: ")
      l.pack(side=LEFT,padx=5, pady=5, fill=X,expand=True)
      l = Label(master=frame,textvariable=var)
      l.pack(side=LEFT,padx=5,pady=5,fill=X,expand=True)
    
  def __on_update(self,category:str,value:str):
    self.__vars[category].set(value)

  def __ignore(self):
    pass

class StreamObservationDiagnosticsWindow(Toplevel):
  __diagnostics_comments: Diagnostics
  __diagnostics_submissions: Diagnostics
  __vars_comments: dict[str,StringVar]
  __vars_submissions: dict[str,StringVar]

  def __init__(self,comments_diagnostics: Diagnostics,submission_diagnostics: Diagnostics,title:str,*args,**kwargs) -> None:
      super().__init__(*args,**kwargs)

      self.__diagnostics_comments = comments_diagnostics
      self.__diagnostics_submissions = submission_diagnostics

      self.__diagnostics_comments.register_to_update(self.__on_update_comments)
      self.__diagnostics_submissions.register_to_update(self.__on_update_submission)

      self.__vars_comments = {}
      self.__vars_submissions = {}
      self.__build(title)

  def __build(self,title:str):
    self.title(title)
    self.protocol("WM_DELETE_WINDOW", self.__ignore)

    lab = Label(master=self,text=title,font=Font(weight=BOLD),relief="groove", borderwidth=1)
    lab.grid(row=0,column=0,columnspan=2)

    submission_frame = Frame(self,relief="groove", borderwidth=1)
    submission_frame.grid(row=1,column=0,padx=5)

    l = Label(master=submission_frame,relief="groove", borderwidth=1,text="From Submissions")
    l.pack(side=TOP,fill=X,pady=5,expand=True)

    self.__build_for_diagnostics(self.__diagnostics_submissions,self.__vars_submissions,submission_frame)

    comments_frame = Frame(self,relief="groove", borderwidth=1)
    comments_frame.grid(row=1,column=1,padx=5)

    l = Label(master=comments_frame,relief="groove", borderwidth=1,text="From Comments")
    l.pack(side=TOP,fill=X,pady=5,expand=True)

    self.__build_for_diagnostics(self.__diagnostics_comments,self.__vars_comments,comments_frame)

  def __build_for_diagnostics(self, diagnostics: Reddit_Crawl_Diagnostics,var_storage: dict[str,StringVar],master):
    for category in diagnostics.categories():
      var = StringVar()
      var_storage[category] = var
      var.set(diagnostics.get(category,as_string=True))
      frame = Frame(master,relief="groove", borderwidth=1)
      frame.pack(side=TOP,fill=X,pady=5,expand=True)

      l = Label(master=frame,text=f"{category}: ")
      l.pack(side=LEFT,padx=5, pady=5, fill=X,expand=True)
      l = Label(master=frame,textvariable=var)
      l.pack(side=LEFT,padx=5,pady=5,fill=X,expand=True)

  def __on_update_comments(self,category:str,value:str):
    self.__vars_comments[category].set(value)
 
  def __on_update_submission(self,category:str,value:str):
    self.__vars_submissions[category].set(value)

  def __ignore(self):
    pass