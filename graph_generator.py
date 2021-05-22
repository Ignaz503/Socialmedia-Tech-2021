from subreddit import Crawl_Metadata, Subreddit_Metadata,Subreddit_Data
from simple_logging import Logger
import math
from colorpallet import ColorPallet
from cancel_token import Cancel_Token
from app_config import Config
import util
import networkx as nx
from networkx import Graph
import numpy as np
from users import UniqueUsers
from networkx.drawing.nx_agraph import write_dot

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
    node['color'] = ColorPallet.SUBREDDIT_COLOR.value 
    __build_title(meta_data,sub_name,node,logger)
    __determine_size_lerp(meta_data,sub_name, node, logger)
    #__determin_size_log(meta_data,sub_name,node)

def __add_meta_to_nodes_sub_sub(graph: Graph, config: Config, logger: Logger, token: Cancel_Token):
  idx_dict = util.define_index_dict_for_subreddits(config.subreddits_to_crawl)
  meta_data = Crawl_Metadata.load()

  for sub_name in config.subreddits_to_crawl:
    idx = idx_dict[sub_name]
    node =  graph.nodes[idx]
    __add_meta_data_to_subreddit_node(meta_data,sub_name,node,logger)

def __add_meta_data_to_edge(edge,min_val: float, max_val: float, min_edge_size: float, max_edge_size:float):
  current_val = float(edge[2]['weight'])
  t = 0.5
  divisor = max_val - min_val
  if not math.isclose(divisor, 0):
    t = (current_val-min_val)/divisor
  
  edge[2]['width'] = ((1.0-t)*min_edge_size) + (t*max_edge_size)
  edge[2]['color'] = ColorPallet.EDGE_COLOR.value
  edge[2]['title'] = edge[2]['weight']

def __add_meta_to_edges_sub_sub(graph: Graph,adj_mat:np.ndarray, config: Config, logger: Logger, token: Cancel_Token, min_edge_size:float = 1, max_edge_size:float = 10):

  min_val = float(adj_mat.min())
  max_val = float(adj_mat.max())

  for edge in graph.edges(data=True):
    __add_meta_data_to_edge(edge,min_val,max_val,min_edge_size,max_edge_size)


def build_graph_subreddit_subreddit(adj_mat: np.ndarray, config: Config, logger:Logger, token: Cancel_Token) -> Graph:
  graph = nx.from_numpy_matrix(adj_mat)
  __add_meta_to_nodes_sub_sub(graph,config,logger,token)
  __add_meta_to_edges_sub_sub(graph,adj_mat,config,logger,token)
  return graph

def __subbdredit_nodes_gnerator(config: Config, logger: Logger, token: Cancel_Token):
  crawl_metadata: Crawl_Metadata = Crawl_Metadata.load()
  counter = 0
  for sub_name in config.subreddits_to_crawl:
    idx = counter
    counter +=1
    if token.is_cancel_requested():
      return
    node = {}
    __add_meta_data_to_subreddit_node(crawl_metadata,sub_name,node,logger)
    yield (idx,node)

def __add_subreddit_nodes(graph: Graph, config: Config, logger: Logger, token: Cancel_Token):
  graph.add_nodes_from(__subbdredit_nodes_gnerator(config,logger,token))

def __user_node_generator(users: UniqueUsers, config: Config, logger: Logger, token: Cancel_Token, user_node_size:float = 5.0):

  counter = len(config.subreddits_to_crawl) # start counter for node id after all subreddits which go from 0 len -1

  for user in users:
    if token.is_cancel_requested():
      return
    idx = counter
    counter+=1
    user_node = {}
    user_node['label'] = user
    user_node['title'] = user
    user_node['color'] = ColorPallet.USER_COLOR.value 
    user_node['size'] = user_node_size
    yield (idx,user_node)

def __add_user_nodes(graph: Graph,users: UniqueUsers, config: Config, logger: Logger, token: Cancel_Token, user_node_size:float = 5.0):
  if token.is_cancel_requested():
    return
  graph.add_nodes_from(__user_node_generator(users,config,logger,token))
    
def __edge_subreddit_user_generator(users: UniqueUsers, config: Config, logger: Logger, token: Cancel_Token):
  idx_dict = util.define_index_dict_for_subreddits(config.subreddits_to_crawl)
  for sub_name in config.subreddits_to_crawl:
    if token.is_cancel_requested():
      return
    sub_data = Subreddit_Data.load(sub_name)
    user_counter = len(config.subreddits_to_crawl) #user nodes start at this index in graph
    for user in users:
      if token.is_cancel_requested():
        return
      user_idx = user_counter
      user_counter += 1
      if sub_data.contains(user):
        yield (idx_dict[sub_name],user_idx,{'color': ColorPallet.EDGE_COLOR.value})

def __add_edges_subreddit_user(graph: Graph, users:UniqueUsers, config: Config, logger: Logger, token: Cancel_Token):
  graph.add_edges_from(__edge_subreddit_user_generator(users,config,logger,token))

def build_graph_subreddit_user(config:Config, logger:Logger, token: Cancel_Token):
  graph: Graph = Graph()
  users = UniqueUsers.load()
  __add_subreddit_nodes(graph,config,logger,token)
  __add_user_nodes(graph,users,config,logger, token)
  if token.is_cancel_requested():
    return graph
  __add_edges_subreddit_user(graph,users, config, logger, token)
  return graph


def write_as_dot(graph: Graph, file_path: str):
  write_dot(graph,file_path)
