import time
from typing import Iterable
import networkx
from networkx.algorithms.operators.binary import intersection
from reddit_crawl.data.subreddit import Crawl_Metadata, Subreddit_Groups, Subreddit_Metadata,Subreddit_Data
from utility.simple_logging import Level, Logger
import math
from utility.colorpallet import DefaultColorPallet
from utility.cancel_token import Cancel_Token
from utility.app_config import Config
import generators.util as util
import networkx as nx
from networkx import Graph
import numpy as np
from reddit_crawl.data.users import MultiSubredditUsers, UniqueUsers
from utility.math import get_hours_minutes_seconds_ms
from networkx.drawing.nx_agraph import write_dot
from generators.data.graph_files import GraphDataFiles

def __determine_size_lerp(meta_data: Crawl_Metadata, subbredit_name: str, node, logger:Logger, min_node_size: float = 10.0, max_node_size:float=50.0):
  t = meta_data.lerp_sub_count(subbredit_name, logger)
  
  node['size'] = ((1.0-t)*min_node_size) + (max_node_size * t)

def __determin_size_log(meta_data: Crawl_Metadata, subbredit_name: str, node, default_size:float = 10, log_base:float = 1.35):
  sub_count = meta_data.get_sub_count(subbredit_name)
  value = default_size
  if sub_count != 0:
    value = math.log(float(sub_count),log_base)
  node['size'] = value

def __build_title(meta_data: Crawl_Metadata, subbredit_name: str, node, logger:Logger):
  sub_data: Subreddit_Metadata = meta_data.data[subbredit_name]
  node['title'] = '<h3>'+subbredit_name +'</h3>'
  node['title'] += sub_data.to_html_string()

def __add_meta_data_to_subreddit_node(meta_data: Crawl_Metadata,sub_name: str,node,logger:Logger):
    node['label'] = sub_name
    node['color'] = DefaultColorPallet.SUBREDDIT_COLOR.value 
    __build_title(meta_data,sub_name,node,logger)
    __determine_size_lerp(meta_data,sub_name, node, logger)
    #__determin_size_log(meta_data,sub_name,node)

def __add_meta_to_nodes_sub_sub(graph: Graph,crawl_metadata:Crawl_Metadata, config: Config, logger: Logger, token: Cancel_Token):
  idx_dict = util.define_index_dict_for_iterable(config.subreddits_to_crawl)

  for sub_name in config.subreddits_to_crawl:
    idx = idx_dict[sub_name]
    node =  graph.nodes[idx]
    __add_meta_data_to_subreddit_node(crawl_metadata,sub_name,node,logger)

def __add_meta_data_to_edge(edge,min_val: float, max_val: float, min_edge_size: float, max_edge_size:float):
  current_val = float(edge[2]['weight'])
  t = 0.5
  divisor = max_val - min_val
  if not math.isclose(divisor, 0):
    t = (current_val-min_val)/divisor
  
  edge[2]['width'] = ((1.0-t)*min_edge_size) + (t*max_edge_size)
  edge[2]['color'] = DefaultColorPallet.EDGE_COLOR.value[0]
  edge[2]['title'] = edge[2]['weight']

def __add_meta_to_edges_sub_sub(graph: Graph,adj_mat:np.ndarray, config: Config, logger: Logger, token: Cancel_Token, min_edge_size:float = 1, max_edge_size:float = 10):
  min_val = float(adj_mat.min())
  max_val = float(adj_mat.max())
  for edge in graph.edges(data=True):
    __add_meta_data_to_edge(edge,min_val,max_val,min_edge_size,max_edge_size)

def build_graph_subreddit_subreddit(adj_mat: np.ndarray,crawl_metadata: Crawl_Metadata, config: Config, logger:Logger, token: Cancel_Token) -> Graph:
  logger.log("building graph subreddit to subreddit")
  graph = nx.from_numpy_matrix(adj_mat)
  logger.log("adding metadata to nodes")
  __add_meta_to_nodes_sub_sub(graph,crawl_metadata, config,logger,token)
  logger.log("adding meta data to edges")
  __add_meta_to_edges_sub_sub(graph,adj_mat,config,logger,token)
  return graph

def __subbdredit_nodes_gnerator(crawl_metadata: Crawl_Metadata, config: Config, logger: Logger, token: Cancel_Token):
  counter = 0
  for sub_name in config.subreddits_to_crawl:
    idx = counter
    counter +=1
    if token.is_cancel_requested():
      return
    node = {}
    __add_meta_data_to_subreddit_node(crawl_metadata,sub_name,node,logger)
    yield (idx,node)

def __add_subreddit_nodes(graph: Graph,crawl_metadata: Crawl_Metadata, config: Config, logger: Logger, token: Cancel_Token):
  graph.add_nodes_from(__subbdredit_nodes_gnerator(crawl_metadata,config,logger,token))

def __user_node_generator(users: Iterable[str],
    start_idx:int, 
    config: Config,
     logger: Logger, 
     token: Cancel_Token, 
     user_node_size:float = 5.0,
    color_option:int = 0):
  counter = start_idx # start counter for node id after all subreddits which go from 0 len -1
  for user in users:
    if token.is_cancel_requested():
      return
    idx = counter
    counter+=1
    user_node = {}
    user_node['label'] = user
    user_node['title'] = user
    user_node['color'] = DefaultColorPallet.USER_COLOR.value[color_option] 
    user_node['size'] = user_node_size
    yield (idx,user_node)

def __add_user_nodes(graph: Graph,users: UniqueUsers, config: Config, logger: Logger, token: Cancel_Token, user_node_size:float = 5.0):
  if token.is_cancel_requested():
    return
  graph.add_nodes_from(__user_node_generator(users,len(config.subreddits_to_crawl),config,logger,token))
    
def __edge_subreddit_user_generator(users: UniqueUsers, config: Config, logger: Logger, token: Cancel_Token):
  idx_dict = util.define_index_dict_for_iterable(config.subreddits_to_crawl)
  for sub_name in config.subreddits_to_crawl:
    if token.is_cancel_requested():
      return
    sub_data = Subreddit_Data.load(sub_name,config)
    user_counter = len(config.subreddits_to_crawl) #user nodes start at this index in graph
    for user in users:
      if token.is_cancel_requested():
        return
      user_idx = user_counter
      user_counter += 1
      if sub_data.contains(user):
        yield (idx_dict[sub_name],user_idx,{'color': DefaultColorPallet.EDGE_COLOR.value[0]})

def __add_edges_subreddit_user(graph: Graph, users:UniqueUsers, config: Config, logger: Logger, token: Cancel_Token):
  graph.add_edges_from(__edge_subreddit_user_generator(users,config,logger,token))

def build_graph_subreddit_user(users:UniqueUsers, crawl_metadata: Crawl_Metadata, config:Config, logger:Logger, token: Cancel_Token): 
  logger.log("building graph subbredit to user")
  graph: Graph = Graph()
  logger.log("adding subreddit nodes")
  __add_subreddit_nodes(graph,crawl_metadata,config,logger,token)
  logger.log("adding user nodes")
  __add_user_nodes(graph,users,config,logger, token)
  if token.is_cancel_requested():
    return graph
  logger.log("adding edges")
  __add_edges_subreddit_user(graph,users, config, logger, token)
    
  return graph

def __edge_generator_user_user_graph(
    mulit_sub_user:MultiSubredditUsers,
    min_intersect_size:int,
    idx_dict:dict[str,int],
    token:Cancel_Token):
  user_list = list(mulit_sub_user.data.keys())
  
  for pair in util.pair_generator(user_list):
    user1, user2 = pair
    intersection = mulit_sub_user.get(user1).intersection(mulit_sub_user.get(user2))

    if len(intersection) >= min_intersect_size: #todo maybe 1 with this approach
      idx1 = idx_dict[user1]
      idx2 = idx_dict[user2]
      yield (idx1,
        idx2,
        {'color': DefaultColorPallet.EDGE_COLOR.value[1],
        'title': str(list(intersection)),
        'width': len(intersection),
        'weight':len(intersection)})

def build_graph_user_user(multi_sub_user: MultiSubredditUsers,
    min_intersect_size:int,
    config:Config,
    logger:Logger,
    token: Cancel_Token):
  start = time.perf_counter()
  graph = Graph()

  idx_dict = util.define_index_dict_for_iterable(multi_sub_user.data.keys())

  logger.log("adding nodes")
  graph.add_nodes_from(__user_node_generator(multi_sub_user.data.keys(),0,config,logger,token,color_option=1))
  logger.log("adding edges")
  graph.add_edges_from(__edge_generator_user_user_graph(multi_sub_user,min_intersect_size,idx_dict,token))
  
  graph.remove_nodes_from(list(networkx.isolates(graph)))

  h,m,s = get_hours_minutes_seconds_ms(time.perf_counter()-start)
  logger.log(f"This took {h}h : {m}m : {s:0.4f}s")
  return graph

def write_as_dot(graph: Graph, file_path: str):
  write_dot(graph,file_path)

def write_all_possible_as_dot(
    users: UniqueUsers,
    crawl_metadata: Crawl_Metadata,
    mat:np.ndarray,
    multi_sub_user: MultiSubredditUsers,
    config: Config,
    logger: Logger,
    token: Cancel_Token): 
  logger.log("generating subreddit subreddit graph")
  g = build_graph_subreddit_subreddit(mat,crawl_metadata,config,logger,token)
  if token.is_cancel_requested():
      return
  write_as_dot(g,GraphDataFiles.SUBREDDIT_SUBREDDIT.get_file_path(config))
  if token.is_cancel_requested():
    return 

  logger.log("generating subreddit user graph")
  g = build_graph_subreddit_user(users,crawl_metadata,config,logger,token)
  if token.is_cancel_requested():
    return
  write_as_dot(g,GraphDataFiles.SUBREDDIT_USER.get_file_path(config))
  if token.is_cancel_requested():
    return
  logger.log("generating user user graphs")
  g = build_graph_user_user(multi_sub_user,2,config,logger,token)
  if g is None:
    return
  write_as_dot(g,GraphDataFiles.USER_USER_MORE_THAN_ONE.get_file_path(config))

  g = build_graph_user_user(multi_sub_user,1,config,logger,token)
  if g is None:
    return
  write_as_dot(g,GraphDataFiles.USER_USER_ONE_OR_MORE.get_file_path(config))

def modify_graph_remove_degree_less_than(graph: Graph, deg:int):
    remove = [node for node,degree in dict(graph.degree()).items() if degree < deg]
    graph.remove_nodes_from(remove)
  