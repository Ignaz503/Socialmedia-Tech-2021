import os
from os import path
from enum import Enum
from utility.app_config import Config

class DataLocation(Enum):
  DEFAULT = "data"
  SUBREDDIT_META = "meta"
  SUBREDDIT = "subreddit"
  VISUALIZATION = "visualization"
  MATRICES = "matrices"
  GRAPHS ="graphs"
  
def __combine_dir_with_default(config:Config,dir:str):
  return path.join(config.get_path_to_storage(),DataLocation.DEFAULT.value,dir)

def ensure_data_locations(config:Config):
  #todo for loop instead of this
  os.makedirs(DataLocation.DEFAULT.value, exist_ok= True)
  os.makedirs(__combine_dir_with_default(config,DataLocation.SUBREDDIT.value), exist_ok= True)
  os.makedirs(__combine_dir_with_default(config,DataLocation.SUBREDDIT_META.value), exist_ok= True)
  os.makedirs(__combine_dir_with_default(config,DataLocation.VISUALIZATION.value), exist_ok= True)
  os.makedirs(__combine_dir_with_default(config,DataLocation.MATRICES.value), exist_ok= True)
  os.makedirs(__combine_dir_with_default(config,DataLocation.GRAPHS.value), exist_ok= True)

def make_data_path(config:Config,filename:str, data_type: DataLocation):
  if data_type is DataLocation.DEFAULT:
    return path.join(config.get_path_to_storage(),DataLocation.DEFAULT.value,filename)
  else:
    return path.join(__combine_dir_with_default(config,data_type.value),filename)

def file_exists(config:Config, filename: str, data_type: DataLocation):
  return path.exists(make_data_path(config,filename,data_type))
