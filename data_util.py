import os
from os import path
from enum import Enum

class DataLocation(Enum):
  DEFAULT = "data"
  SUBREDDIT_META = "meta"
  SUBREDDIT = "subreddit"
  VISUALIZATION = "visualization"
  
def __combine_dir_with_default(dir:str):
  return path.join(DataLocation.DEFAULT.value,dir)

def ensure_data_locations():
  os.makedirs(DataLocation.DEFAULT.value, exist_ok= True)
  os.makedirs(__combine_dir_with_default(DataLocation.SUBREDDIT.value), exist_ok= True)
  os.makedirs(__combine_dir_with_default(DataLocation.SUBREDDIT_META.value), exist_ok= True)
  os.makedirs(__combine_dir_with_default(DataLocation.VISUALIZATION.value), exist_ok= True)

def make_data_path(filename:str, data_type: DataLocation):
  if data_type is DataLocation.DEFAULT:
    return path.join(DataLocation.DEFAULT.value,filename)
  else:
    return path.join(__combine_dir_with_default(data_type.value),filename)

def file_exists(filename: str, data_type: DataLocation):
  return path.exists(make_data_path(filename,data_type))
