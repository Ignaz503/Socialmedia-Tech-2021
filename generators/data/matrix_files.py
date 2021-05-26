from typing import Union
from utility.app_config import Config
import utility.data_util as data_util
from utility.data_util import DataLocation
from enum import Enum
import numpy as np

class MatrixFiles(Enum):
  SUBREDDIT_SUBREDDIT = "subreddit_subreddit.csv"
  SUBREDDIT_USER = "subreddit_user.csv"
  USER_USER = "user_user.csv"

  def get_file_path(self, config:Config):
    return data_util.make_data_path(config,self.value,DataLocation.MATRICES)

  def load(self,config:Config) -> np.ndarray:
    path = self.get_file_path(config)
    return np.loadtxt(fname= path, dtype=np.int32, delimiter=",",skiprows = 1)