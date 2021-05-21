import threading
from cancel_token import Cancel_Token
from subreddit import Crawl_Metadata, Subreddit_Metadata
import util
import data_util
import numpy as np
import networkx as nx
import data_generator as dg
from app_config import Config
from simple_logging import Logger
from pyvis.network import Network
from data_util import DataLocation
from networkx.classes.graph import Graph
import math

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

def __add_meta_to_nodes(graph: Graph, config: Config, logger: Logger, token: Cancel_Token):
  idx_dict = util.define_index_dict_for_subreddits(config.subreddits_to_crawl)
  meta_data = Crawl_Metadata.load(config.meta_data_name)

  for sub_name in config.subreddits_to_crawl:
    idx = idx_dict[sub_name]
    node =  graph.nodes[idx]
    node['label'] = sub_name
    node['color'] = "#e94560" 
    __build_title(meta_data,sub_name,node,logger)
    __determine_size_lerp(meta_data,sub_name, node, logger)
    #__determin_size_log(meta_data,sub_name,node)

def __add_meta_to_edges(graph: Graph,adj_mat:np.ndarray, config: Config, logger: Logger, token: Cancel_Token, min_edge_size:float = 1, max_edge_size:float = 10):

  min_val = float(adj_mat.min())
  max_val = float(adj_mat.max())

  for edge in graph.edges(data=True):
    current_val = float(edge[2]['weight'])
    t = 0.5
    divisor = max_val - min_val
    if not math.isclose(divisor, 0):
      t = (current_val-min_val)/divisor
    
    edge[2]['width'] = ((1.0-t)*min_edge_size) + (t*max_edge_size)
    edge[2]['color'] ="#3e5c7f"
    edge[2]['title'] = edge[2]['weight']

def __build_graph(adj_mat: np.ndarray, config: Config, logger:Logger, token: Cancel_Token) -> Graph:
  graph = nx.from_numpy_matrix(adj_mat)
  __add_meta_to_nodes(graph,config,logger,token)
  __add_meta_to_edges(graph,adj_mat,config,logger,token)
  return graph

def __visualize(adj_mat: np.ndarray, config: Config, logger:Logger, token: Cancel_Token):
  graph = __build_graph(adj_mat,config,logger,token)

  vis_network = Network('1920px','1920px',bgcolor="#121220",font_color="#fefefe")
  vis_network.from_nx(graph)
  vis_network.hrepulsion()
  vis_network.toggle_physics(False)
  vis_network.show_buttons(filter_=['nodes', 'edges', 'layout', 'interaction', 'manipulation', 'selection', 'renderer'])

  name = data_util.make_data_path(config.visualization_name,  DataLocation.VISUALIZATION)
  logger.log("showing visualization {n}".format(n=config.visualization_name))
  vis_network.show(name)

def __generate_and_visualize(config: Config, logger:Logger, token: Cancel_Token):
  with token:
    mat = dg.generate_adjacency_mat(config,logger,token)
    print(mat)
    if token.is_cancel_requested():
      logger.log("canceling")
      return
    __visualize(mat,config,logger,token)

def run(config: Config, logger: Logger, token: Cancel_Token):
  thread = threading.Thread(name="visualize thread", target=__generate_and_visualize,args=(config,logger,token))
  thread.start()

