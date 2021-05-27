import random
import time
from typing import Any, Iterable
import numpy as np
from utility.app_config import Config
from utility.simple_logging import Logger, Level
from utility.cancel_token import Cancel_Token
from reddit_crawl.data.subreddit import Subreddit_Data
from reddit_crawl.data.users import MultiSubredditUsers, UniqueUsers

def define_index_dict_for_iterable(to_idx: Iterable[str]) -> dict[str,int]:
  idx_dict = {}
  count = 0
  for sub in to_idx:
    idx_dict[sub] = count
    count +=1
  return idx_dict

def random_adjacency_mat(size:int, likelyhood:  float) -> np.ndarray:
  arr = np.zeros((size,size), dtype=np.int32)
  for i in range(0,size):
    for j in range(0,size):
      if i == j:
        continue
      if random.random() <= likelyhood:
        arr[i,j] += 1
        arr[j,i] += 1
  return arr

def generate_sub_sub_mat_and_multi_sub_user_metadata(config: Config, logger: Logger, token: Cancel_Token)-> tuple[np.ndarray,MultiSubredditUsers]:
  logger.log("starting to generate adjacency matrix subreddit to subreddit")
  index_dict = define_index_dict_for_iterable(config.subreddits_to_crawl)
  size = len(config.subreddits_to_crawl)
  adjacency_mat = np.zeros((size,size), dtype=np.int32)
  multi_sub_users = MultiSubredditUsers.load(config)
  for pair in pair_generator(config.subreddits_to_crawl):
    if token.is_cancel_requested():
      break
    logger.log(f"[Sub Sub Adj Mat] handling subreddit pair ({pair[0]},{pair[1]})")
    __update_adjacency_matrix(index_dict,pair,adjacency_mat,multi_sub_users,config)
  return (adjacency_mat,multi_sub_users)

def pair_generator(some_list:list[str]):
  for i in range(len(some_list)):
    for j in range(i+1, len(some_list)):
      yield (some_list[i],some_list[j])

def __update_adjacency_matrix(index_dict: dict[str,int], pair: tuple[str,str], adjacency_mat: np.ndarray, multi_sub_users:MultiSubredditUsers,config:Config):
  sub_one: Subreddit_Data = Subreddit_Data.load(pair[0],config)
  sub_two: Subreddit_Data = Subreddit_Data.load(pair[1],config) 
  idx_one = index_dict[pair[0]]
  idx_two = index_dict[pair[1]]

  intersection =sub_one.users.intersection(sub_two.users)
  intersection_size = len(intersection)

  for user in intersection:
    multi_sub_users.add_or_update_user(user,(sub_one.name, sub_two.name))

  adjacency_mat[idx_one,idx_two] = intersection_size
  adjacency_mat[idx_two,idx_one] = intersection_size

def generate_sub_user_adjacency_mat(config: Config, logger: Logger, token: Cancel_Token)-> np.ndarray:
  logger.log("generating subrredit to user adjacency matrix",Level.INFO)
  index_dict = define_index_dict_for_iterable(config.subreddits_to_crawl)
  users = UniqueUsers.load(config)
  cols = len(config.subreddits_to_crawl)
  rows = users.count()

  if cols == 0 or rows == 0:
    return None

  logger.log("creating matrix of size {r}x{c}".format(r=rows,c=cols),Level.INFO)
  mat = np.zeros((rows,cols), dtype= np.int32)

  for sub_name in config.subreddits_to_crawl:
    sub: Subreddit_Data = Subreddit_Data.load(sub_name,config)
    user_idx = 0
    for user in users.data:
      if sub.contains(user):
          mat[user_idx,index_dict[sub_name]]+=1
      user_idx +=1

  return mat