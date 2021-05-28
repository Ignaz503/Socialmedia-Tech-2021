from enum import Enum
import os
import platform
import  subprocess
from utility.app_config import Config
import utility.data_util as data_util
from utility.data_util import DataLocation

class VisualizationDataFile:
  name:str
  def __init__(self,name) -> None:
      self.name = name

  def get_file_path(self, config: Config):
    return data_util.make_data_path(config,self.name,  DataLocation.VISUALIZATION)

  def show(self,config:Config):
    filepath = os.path.join(os.getcwd(),self.get_file_path(config))

    if platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', filepath))
    elif platform.system() == 'Windows':    # Windows
        os.startfile(filepath)
    else:                                   # linux variants
        subprocess.call(('xdg-open', filepath))