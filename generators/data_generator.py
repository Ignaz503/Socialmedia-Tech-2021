from reddit_crawl.data.users import UniqueUsers
from utility.cancel_token import Cancel_Token
import threading
import generators.util as util
import utility.data_util as data_util
import numpy as np
from utility.app_config import Config
from utility.simple_logging import Logger, Level
from utility.data_util import DataLocation
import reddit_crawl.meta_data_crawl as rmdc
from reddit_crawl.data.subreddit import Crawl_Metadata, Subreddit_Data
import generators.graph_generator as graph_generator

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
    mat = util.generate_sub_sub_adjacency_mat(config,logger,token)
    if token.is_cancel_requested():
      return
    __save_adjacency_mat(mat, "subreddit_subreddit.csv",logger, token)
    if token.is_cancel_requested():
      return
    mat = util.generate_sub_user_adjacency_mat(config,logger,token)
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
    graph_generator.write_all_possible_as_dot(config,logger,token)
    logger.log("data generation done")


def run(config: Config, logger: Logger, token: Cancel_Token):
  thread = threading.Thread(name="data generation thread",target=__execute_generating,args=(config,logger,token))
  thread.start()
