from app_config import Config
from simple_logging import Logger
import subreddit
from subreddit import Subreddit_Data
import defines

def sub_pairs(subs:list[str]):
  return [(subs[i],subs[j]) for i in range(len(subs)) for j in range(i+1, len(subs))]
 
def define_index_dict(subs: list[str]):
  idx_dict = {}
  count = 0
  for sub in subs:
    idx_dict[sub] = count
    count +=1
  return idx_dict

def update_adjacency_matrix(index_dict: dict[str,int], pair: tuple[str,str], adjacency_mat):
  sub_one: Subreddit_Data = subreddit.load(defines.DATA_BASE_PATH,pair[0])
  sub_two: Subreddit_Data = subreddit.load(defines.DATA_BASE_PATH,pair[1]) 
  #loop over users, check if other has same user, if yes note in adjacency matrix, else continue
  raise NotImplementedError()

def save(adjacency_mat):
  #todo
  raise NotImplementedError()

def run(config: Config, logger: Logger):
  index_dict = define_index_dict(config.subreddits_to_crawl)
  adjacency_mat = {} #todo numpy
  for pair in sub_pairs(config.subreddits_to_crawl):
    update_adjacency_matrix(index_dict,pair,adjacency_mat)
  save(adjacency_mat)
