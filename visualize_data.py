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

def __determine_size(meta_data: Crawl_Metadata, subbredit_name: str, node, logger:Logger, default_size: float = 10.0):
  t = meta_data.lerp_sub_count(subbredit_name, logger)
  t += 0.5 # move from 0..1 to 0.5 to 1.5
  node['size'] = default_size * t

def __build_title(meta_data: Crawl_Metadata, subbredit_name: str, node, logger:Logger):
  sub_data: Subreddit_Metadata = meta_data.data[subbredit_name]
  node['title'] = '<h3>'+subbredit_name +'</h3>'
  node['title'] += sub_data.to_html_string()

def __add_meta_to_nodes(graph: Graph, config: Config, logger: Logger):
  idx_dict = util.define_index_dict_for_subreddits(config.subreddits_to_crawl)
  meta_data = Crawl_Metadata.load(config.meta_data_name)

  for sub_name in config.subreddits_to_crawl:
    idx = idx_dict[sub_name]
    node =  graph.nodes[idx]
    node['label'] = sub_name
    __build_title(meta_data,sub_name,node,logger)
    __determine_size(meta_data,sub_name, node, logger)

def __build_graph(adj_mat: np.ndarray, config: Config, logger:Logger) -> Graph:
  graph = nx.from_numpy_matrix(adj_mat)
  __add_meta_to_nodes(graph,config,logger)
  return graph

def __visualize(adj_mat: np.ndarray, config: Config, logger:Logger):
  graph = __build_graph(adj_mat,config,logger)
  vis_network = Network('1920px','1920px',bgcolor="#121220",font_color="#fefefe")
  vis_network.from_nx(graph)
  vis_network.toggle_physics(False)
  vis_network.show_buttons(filter_=['nodes', 'edges', 'layout', 'interaction', 'manipulation', 'selection', 'renderer'])

  for node in vis_network.nodes:
    node['color'] = "#e94560" 
  
  for edge in vis_network.edges:
    edge['color'] ="#3e5c7f"
  name = data_util.make_data_path(config.visualization_name,  DataLocation.VISUALIZATION)
  print(name)
  vis_network.show(name)

def __generate_and_visualize(config: Config, logger:Logger):
  mat = dg.generate_adjacency_mat(config,logger)
  #mat = util.random_adjacency_mat(10,.25)
  __visualize(mat,config,logger)

def run(config: Config, logger: Logger):
  __generate_and_visualize(config,logger)

