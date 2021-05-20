from networkx.classes.graph import Graph
from app_config import Config
from simple_logging import Logger
from typing import Any
import numpy as np
import data_generator as dg
from os import path
import util
import networkx as nx
from pyvis.network import Network
from defines import VIS_NAME

def __build_graph(adj_mat: np.ndarray, config: Config, logger:Logger) -> Graph:
  graph = nx.from_numpy_matrix(adj_mat)
  #todo give nodes name and sizes 
  return graph

def __visualize(adj_mat: np.ndarray, config: Config, logger:Logger):
  graph = __build_graph(adj_mat,config,logger)
  vis_network = Network('1920px','1080px',bgcolor="#121220",font_color="#fefefe")
  vis_network.from_nx(graph)
  vis_network.toggle_physics(False)
  vis_network.show_buttons(filter_=['nodes', 'edges', 'layout', 'interaction', 'manipulation', 'selection', 'renderer'])
  
  for node in vis_network.nodes:
    node['color'] = "#e94560" 
  
  for edge in vis_network.edges:
    edge['color'] ="#3e5c7f"

  vis_network.show(util.make_data_path(VIS_NAME))

def __generate_and_visualize(config: Config, logger:Logger):
  #mat = dg.generate_adjacency_mat(config,logger)
  mat = util.random_adjacency_mat(10,.25)
  __visualize(mat,config,logger)

def run(config: Config, logger: Logger):
  __generate_and_visualize(config,logger)

