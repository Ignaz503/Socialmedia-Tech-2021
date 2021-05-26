from enum import Enum
import os
import platform
import  subprocess
from utility.app_config import Config
import utility.data_util as data_util
from utility.data_util import DataLocation

class VisualizationDataFiles(Enum):
  SUBREDDIT_SUBREDDIT = "reddit_visualization_subreddit_subreddit.html"
  SUBBREDDIT_SUBBREDIT_COLORING_CLUSTER = "reddit_visualization_subreddit_subreddit_coloring_cluster.html"
  SUBREDDIT_USER = "reddit_visualization_subreddit_user.html"
  USER_USER = "reddit_visualization_user_user.html"

  def get_file_path(self, config: Config):
    return data_util.make_data_path(config,self.value,  DataLocation.VISUALIZATION)

  def show(self,config:Config):
    filepath = os.path.join(os.getcwd(),self.get_file_path(config))

    if platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', filepath))
    elif platform.system() == 'Windows':    # Windows
        os.startfile(filepath)
    else:                                   # linux variants
        subprocess.call(('xdg-open', filepath))

  @staticmethod
  def from_name(name:str):
    for t in VisualizationDataFiles:
      if t.name == name:
        return t
    raise ValueError(f"{name} is not a valid VisualizationDataFiles name")
