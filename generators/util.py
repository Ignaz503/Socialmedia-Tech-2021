import random
import numpy as np
from utility.app_config import Config
from utility.simple_logging import Logger, Level
from utility.cancel_token import Cancel_Token
from reddit_crawl.data.subreddit import Subreddit_Data
from reddit_crawl.data.users import UniqueUsers


def define_index_dict_for_subreddits(subs: list[str]) -> dict[str,int]:
  idx_dict = {}
  count = 0
  for sub in subs:
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


def generate_sub_sub_adjacency_mat(config: Config, logger: Logger, token: Cancel_Token)-> np.ndarray:
  logger.log("starting to generate adjacency matrix subreddit to subreddit")
  index_dict = define_index_dict_for_subreddits(config.subreddits_to_crawl)
  size = len(config.subreddits_to_crawl)
  adjacency_mat = np.zeros((size,size), dtype=np.int32)
  for pair in __sub_pairs(config.subreddits_to_crawl):
    if token.is_cancel_requested():
      break
    logger.log(f"handling subreddit pair ({pair[0]},{pair[1]})")
    __update_adjacency_matrix(index_dict,pair,adjacency_mat)
  return adjacency_mat

def __sub_pairs(subs:list[str]):
  return [(subs[i],subs[j]) for i in range(len(subs)) for j in range(i+1, len(subs))]
 
def __update_adjacency_matrix(index_dict: dict[str,int], pair: tuple[str,str], adjacency_mat: np.ndarray):
  sub_one: Subreddit_Data = Subreddit_Data.load(pair[0])
  sub_two: Subreddit_Data = Subreddit_Data.load(pair[1]) 
  idx_one = index_dict[pair[0]]
  idx_two = index_dict[pair[1]]
  intersection_size = len(sub_one.users.intersection(sub_two.users))
  adjacency_mat[idx_one,idx_two] = intersection_size
  adjacency_mat[idx_two,idx_one] = intersection_size

def generate_sub_user_adjacency_mat(config: Config, logger: Logger, token: Cancel_Token)-> np.ndarray:
  logger.log("generating subrredit to user adjacency matrix",Level.INFO)
  index_dict = define_index_dict_for_subreddits(config.subreddits_to_crawl)
  users = UniqueUsers.load()
  cols = len(config.subreddits_to_crawl)
  rows = users.count()

  if cols == 0 or rows == 0:
    return None

  logger.log("creating matrix of size {r}x{c}".format(r=rows,c=cols),Level.INFO)
  mat = np.zeros((rows,cols), dtype= np.int32)

  for sub_name in config.subreddits_to_crawl:
    sub: Subreddit_Data = Subreddit_Data.load(sub_name)
    user_idx = 0
    for user in users.data:
      if sub.contains(user):
          mat[user_idx,index_dict[sub_name]]+=1
      user_idx +=1

  return mat