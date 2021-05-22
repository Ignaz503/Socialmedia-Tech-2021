from users import UniqueUsers
from cancel_token import Cancel_Token
import threading
import util
import data_util
import numpy as np
from app_config import Config
from simple_logging import Level, Logger
from data_util import DataLocation
import reddit_meta_data_crawl as rmdc
from subreddit import Crawl_Metadata, Subreddit_Data
import graph_generator

__SUBREDDIT_SUBREDDIT_GRAPH = "subreddit_subreddit.dot"
__SUBREDDIT_USER_GRAPH = "subreddit_user.dot"

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

def __save_adjacency_mat(adjacency_mat: np.ndarray, name:str,logger:Logger, token: Cancel_Token):
  if adjacency_mat is None:
    logger.log("matrix object is none, cannot save to disk",Level.WARNING)
    return
  logger.log("Saving adjacency matrix {n} to disk".format(n=name), Level.INFO)
  header ="{mi}, {ma}".format(mi= adjacency_mat.min(),ma=adjacency_mat.max())
  np.savetxt(data_util.make_data_path(name,DataLocation.MATRICES),adjacency_mat,fmt="%i", delimiter=",", header=header)

def __save_meta_data(meta_data: Crawl_Metadata, config: Config, logger: Logger, token: Cancel_Token):
  logger.log("Saving metadata to disk",Level.INFO)
  meta_data.save_to_file()

def generate_sub_sub_adjacency_mat(config: Config, logger: Logger, token: Cancel_Token)-> np.ndarray:
  index_dict = util.define_index_dict_for_subreddits(config.subreddits_to_crawl)
  size = len(config.subreddits_to_crawl)
  adjacency_mat = np.zeros((size,size), dtype=np.int32)
  for pair in __sub_pairs(config.subreddits_to_crawl):
    if token.is_cancel_requested():
      break
    __update_adjacency_matrix(index_dict,pair,adjacency_mat)
  return adjacency_mat

def generate_sub_user_adjacency_mat(config: Config, logger: Logger, token: Cancel_Token)-> np.ndarray:
  logger.log("generating subrredit to user adjacency matrix",Level.INFO)
  index_dict = util.define_index_dict_for_subreddits(config.subreddits_to_crawl)
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

def __generate_meta_data(config: Config, logger: Logger, token: Cancel_Token) -> Crawl_Metadata:
  md_c = Crawl_Metadata.load()
  rmdc.run(md_c,config,logger,token)
  return md_c

def __generate_unique_user(config: Config, logger: Logger, token: Cancel_Token) -> UniqueUsers:
  logger.log("genrating unqiue user list", Level.INFO)
  users: UniqueUsers = UniqueUsers.load()
  for sub_name in config.subreddits_to_crawl:
    sub_data = Subreddit_Data.load(sub_name)
    users.add_users(sub_data.users)
  logger.log("found {c} unique users from {cs} subreddits".format(c=users.count(),cs = len(config.subreddits_to_crawl)),Level.INFO)
  return users

def __save_unique_user_list(users: UniqueUsers):
  users.save_to_file()

def __execute_generating(config: Config, logger: Logger, token: Cancel_Token):
  #this might be the uggliest function i have ever writen
  logger.log("generating data",Level.INFO)
  with token:
    mat = generate_sub_sub_adjacency_mat(config,logger,token)
    if token.is_cancel_requested():
      return
    __save_adjacency_mat(mat, "subreddit_subreddit.csv",logger, token)
    if token.is_cancel_requested():
      return
    g = graph_generator.build_graph_subreddit_subreddit(mat,config,logger,token)
    if token.is_cancel_requested():
      return
    graph_generator.write_as_dot(g,data_util.make_data_path(__SUBREDDIT_SUBREDDIT_GRAPH,DataLocation.GRAPHS))
    if token.is_cancel_requested():
      return
    if token.is_cancel_requested():
      return
    mat = generate_sub_user_adjacency_mat(config,logger,token)
    if token.is_cancel_requested():
      return
    __save_adjacency_mat(mat,"subreddit_user.csv",logger,token)
    if token.is_cancel_requested():
      return
    md = __generate_meta_data(config,logger,token)
    if token.is_cancel_requested():
      return
    __save_meta_data(md,config,logger,token)
    if token.is_cancel_requested():
      return
    users = __generate_unique_user(config,logger,token)
    if token.is_cancel_requested():
      return
    __save_unique_user_list(users)
    if token.is_cancel_requested():
      return
    g = graph_generator.build_graph_subreddit_user(config,logger,token)
    if token.is_cancel_requested():
      return
    graph_generator.write_as_dot(g,data_util.make_data_path(__SUBREDDIT_USER_GRAPH,DataLocation.GRAPHS))
    logger.log("data generation done")


def run(config: Config, logger: Logger, token: Cancel_Token):
  thread = threading.Thread(name="data generation thread",target=__execute_generating,args=(config,logger,token))
  thread.start()
