from app_config import Config
from simple_logging import Logger
import subreddit
from subreddit import Subreddit_Data
from defines import DATA_BASE_PATH, ADJACENCY_MAT
from os import path
import numpy as np
import util

def __sub_pairs(subs:list[str]):
  return [(subs[i],subs[j]) for i in range(len(subs)) for j in range(i+1, len(subs))]
 
def __update_adjacency_matrix(index_dict: dict[str,int], pair: tuple[str,str], adjacency_mat: np.ndarray):
  sub_one: Subreddit_Data = subreddit.load(pair[0])
  sub_two: Subreddit_Data = subreddit.load(pair[1]) 
  idx_one = index_dict[pair[0]]
  idx_two = index_dict[pair[0]]
  intersection_size = len(sub_one.users.intersection(sub_two.users))
  adjacency_mat[idx_one,idx_two] = intersection_size
  adjacency_mat[idx_two,idx_one] = intersection_size

def __save(adjacency_mat: np.ndarray):
  header ="{mi}, {ma}".format(mi= adjacency_mat.min(),ma=adjacency_mat.max())
  np.savetxt(path.join(DATA_BASE_PATH,ADJACENCY_MAT),adjacency_mat,fmt="%i", delimiter=",", header=header)

def generate_adjacency_mat(config: Config, logger: Logger)-> np.ndarray:
  index_dict = util.define_index_dict_for_adj_mat(config.subreddits_to_crawl)
  size = len(config.subreddits_to_crawl)
  adjacency_mat = np.zeros((size,size), dtype=np.int32)
  for pair in __sub_pairs(config.subreddits_to_crawl):
    __update_adjacency_matrix(index_dict,pair,adjacency_mat)
  return adjacency_mat

def run(config: Config, logger: Logger):
  adjacency_mat = generate_adjacency_mat(config,logger)
  __save(adjacency_mat)
