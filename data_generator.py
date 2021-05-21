from cancel_token import Cancel_Token
import threading
import util
import subreddit
import data_util
import numpy as np
from app_config import Config
from simple_logging import Logger
from defines import ADJACENCY_MAT
from data_util import DataLocation
import reddit_meta_data_crawl as rmdc
from subreddit import Crawl_Metadata, Subreddit_Data

def __sub_pairs(subs:list[str]):
  return [(subs[i],subs[j]) for i in range(len(subs)) for j in range(i+1, len(subs))]
 
def __update_adjacency_matrix(index_dict: dict[str,int], pair: tuple[str,str], adjacency_mat: np.ndarray):
  sub_one: Subreddit_Data = Subreddit_Data.load(pair[0])
  sub_two: Subreddit_Data = Subreddit_Data.load(pair[1]) 
  idx_one = index_dict[pair[0]]
  idx_two = index_dict[pair[0]]
  intersection_size = len(sub_one.users.intersection(sub_two.users))
  adjacency_mat[idx_one,idx_two] = intersection_size
  adjacency_mat[idx_two,idx_one] = intersection_size

def __save_adjacency_mat(adjacency_mat: np.ndarray, token: Cancel_Token):
  header ="{mi}, {ma}".format(mi= adjacency_mat.min(),ma=adjacency_mat.max())
  np.savetxt(data_util.make_data_path(ADJACENCY_MAT,DataLocation.DEFAULT),adjacency_mat,fmt="%i", delimiter=",", header=header)

def __save_meta_data(meta_data: Crawl_Metadata, config: Config, logger: Logger, token: Cancel_Token):
  logger.log("Saving metadata to disk")
  meta_data.save_to_file(config.meta_data_name)

def generate_adjacency_mat(config: Config, logger: Logger, token: Cancel_Token)-> np.ndarray:
  index_dict = util.define_index_dict_for_subreddits(config.subreddits_to_crawl)
  size = len(config.subreddits_to_crawl)
  adjacency_mat = np.zeros((size,size), dtype=np.int32)
  for pair in __sub_pairs(config.subreddits_to_crawl):
    if token.is_cancel_requested():
      break
    __update_adjacency_matrix(index_dict,pair,adjacency_mat)
  return adjacency_mat

def generate_meta_data(config: Config, logger: Logger, token: Cancel_Token) -> Crawl_Metadata:
  md_c = Crawl_Metadata.load(config.meta_data_name)
  rmdc.run(md_c,config,logger,token)
  return md_c

def __execute_generating(config: Config, logger: Logger, token: Cancel_Token):
  logger.log("generating data")
  with token:
    mat = generate_adjacency_mat(config,logger,token)
    if token.is_cancel_requested():
      return
    __save_adjacency_mat(mat ,token)
    if token.is_cancel_requested():
      return
    md = generate_meta_data(config,logger,token)
    if token.is_cancel_requested():
      return
    __save_meta_data(md,config,logger,token)

def run(config: Config, logger: Logger, token: Cancel_Token):
  thread = threading.Thread(name="data generation thread",target=__execute_generating,args=(config,logger,token))
  thread.start()
