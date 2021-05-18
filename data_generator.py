from app_config import Config
from simple_logging import Logger
import subreddit
from subreddit import Subreddit_Data
from defines import DATA_BASE_PATH, ADJACENCY_MAT
from os import path
import numpy as np

def sub_pairs(subs:list[str]):
  return [(subs[i],subs[j]) for i in range(len(subs)) for j in range(i+1, len(subs))]
 
def define_index_dict(subs: list[str]):
  idx_dict = {}
  count = 0
  for sub in subs:
    idx_dict[sub] = count
    count +=1
  return idx_dict

def update_adjacency_matrix(index_dict: dict[str,int], pair: tuple[str,str], adjacency_mat: np.ndarray):
  sub_one: Subreddit_Data = subreddit.load(DATA_BASE_PATH,pair[0])
  sub_two: Subreddit_Data = subreddit.load(DATA_BASE_PATH,pair[1]) 
  idx_one = index_dict[pair[0]]
  idx_two = index_dict[pair[0]]
  intersection_size = len(sub_one.users.intersection(sub_two.users))
  adjacency_mat[idx_one,idx_two] = intersection_size
  adjacency_mat[idx_two,idx_one] = intersection_size

def save(adjacency_mat: np.ndarray):
  header ="{mi}, {ma}".format(mi= adjacency_mat.min(),ma=adjacency_mat.max())
  np.savetxt(path.join(DATA_BASE_PATH,ADJACENCY_MAT),adjacency_mat,fmt="%i", delimiter=",", header=header)

def run(config: Config, logger: Logger):
  index_dict = define_index_dict(config.subreddits_to_crawl)
  logger.log(index_dict)
  size = len(config.subreddits_to_crawl)
  adjacency_mat = np.zeros((size,size), dtype=np.int32)
  for pair in sub_pairs(config.subreddits_to_crawl):
    update_adjacency_matrix(index_dict,pair,adjacency_mat)
  save(adjacency_mat)
