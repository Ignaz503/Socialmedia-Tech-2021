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

def __save_adjacency_mat(adjacency_mat: np.ndarray):
  header ="{mi}, {ma}".format(mi= adjacency_mat.min(),ma=adjacency_mat.max())
  np.savetxt(data_util.make_data_path(ADJACENCY_MAT,DataLocation.DEFAULT),adjacency_mat,fmt="%i", delimiter=",", header=header)

def __save_meta_data(meta_data: Crawl_Metadata, config: Config, logger: Logger):
  logger.log("Saving metadata to disk")
  meta_data.save_to_file(config.meta_data_name)

def generate_adjacency_mat(config: Config, logger: Logger)-> np.ndarray:
  index_dict = util.define_index_dict_for_subreddits(config.subreddits_to_crawl)
  size = len(config.subreddits_to_crawl)
  adjacency_mat = np.zeros((size,size), dtype=np.int32)
  for pair in __sub_pairs(config.subreddits_to_crawl):
    __update_adjacency_matrix(index_dict,pair,adjacency_mat)
  return adjacency_mat

def generate_meta_data(config: Config, logger: Logger) -> Crawl_Metadata:
  md_c = Crawl_Metadata.load(config.meta_data_name)
  rmdc.run(md_c,config,logger)
  return md_c

def run(config: Config, logger: Logger):
  logger.log("generating data")
  __save_adjacency_mat( generate_adjacency_mat(config,logger))
  __save_meta_data(generate_meta_data(config,logger),config,logger)
