import os
from os import path
from enum import Enum

class DataLocation(Enum):
  DEFAULT = "data"
  SUBREDDIT_META = "meta"
  SUBREDDIT = "subreddit"
  VISUALIZATION = "visualization"
  MATRICES = "matrices"
  GRAPHS ="graphs"
  LOG = "log"
  
def __combine_dir_with_default(config,dir:str):
  return path.join(config.get_path_to_storage(),DataLocation.DEFAULT.value,dir)

def __combine_dir_with_default_str(base_path:str,dir:str):
  return path.join(base_path,DataLocation.DEFAULT.value,dir)

def ensure_data_locations(config):
  #todo for loop instead of this
  for e in DataLocation:
    if e is DataLocation.DEFAULT:
      os.makedirs(DataLocation.DEFAULT.value, exist_ok= True)
    else:
      os.makedirs(__combine_dir_with_default(config,e.value), exist_ok= True)

def make_data_path(config,filename:str, location: DataLocation):
  if location is DataLocation.DEFAULT:
    return path.join(config.get_path_to_storage(),DataLocation.DEFAULT.value,filename)
  else:
    return path.join(__combine_dir_with_default(config,location.value),filename)

def make_data_path_str(base_path:str,filename:str,location:DataLocation):
  if location is DataLocation.DEFAULT:
    return path.join(base_path,DataLocation.DEFAULT.value,filename)
  else:
    return path.join(__combine_dir_with_default_str(base_path,location.value),filename)


def file_exists(config, filename: str, data_type: DataLocation):
  return path.exists(make_data_path(config,filename,data_type))
