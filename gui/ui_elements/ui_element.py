from tkinter import Frame

class UIElement(Frame):
  def __init__(self, application,*args, **kwargs) -> None:
      super().__init__(*args, **kwargs)
      self.application = application
      self._build()
  
  def _build(self):
    pass
  