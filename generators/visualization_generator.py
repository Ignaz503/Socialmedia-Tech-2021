from math import log
import threading
from typing import Callable
import generators.graph_generator as gg
from utility.cancel_token import Cancel_Token
import utility.data_util as data_util
import numpy as np
import generators.util as dg
from utility.app_config import Config
from utility.simple_logging import Logger, Level
from pyvis.network import Network
from utility.data_util import DataLocation
from networkx.classes.graph import Graph
from utility.colorpallet import ColorPallet

SUBREDDIT_SUBREDDIT_VISUALIZATION_NAME = "reddit_visualization_subreddit_subreddit.html"
SUBREDDIT_USER_VISUALIZATION_NAME ="reddit_visualization_subreddit_user.html"

def __build_network_from_graph(graph: Graph,physics: bool, buttons_filter=[])->Network:
  vis_network = Network('1920px','1920px',bgcolor=ColorPallet.BACKGROUND_COLOR.value,font_color=ColorPallet.FONT_COLOR.value)
  vis_network.from_nx(graph)
  vis_network.force_atlas_2based()
  vis_network.toggle_physics(physics)
  vis_network.show_buttons(filter_=buttons_filter)
  return vis_network

def __visualize_subreddit_subreddit(adj_mat: np.ndarray, config: Config, logger:Logger, token: Cancel_Token):
  logger.log("viusalizing subreddit to subreddit graph")
  graph = gg.build_graph_subreddit_subreddit(adj_mat,config,logger,token)
  if token.is_cancel_requested():
    return
  logger.log("creating visualization")
  vis_network = __build_network_from_graph(graph,False,['nodes', 'edges', 'layout', 'interaction', 'manipulation', 'selection', 'renderer'])

  name = data_util.make_data_path(SUBREDDIT_SUBREDDIT_VISUALIZATION_NAME,  DataLocation.VISUALIZATION)
  logger.log("saving visualization {n}".format(n=SUBREDDIT_SUBREDDIT_VISUALIZATION_NAME), Level.INFO)
  vis_network.save_graph(name)
  

def __visualize_subreddit_user(config: Config, logger:Logger, token: Cancel_Token):
  logger.log("visulaizting subreddit user graph")
  graph = gg.build_graph_subreddit_user(config,logger,token)

  logger.log("creating visualization")
  vis_network = __build_network_from_graph(graph,True,['physics'])

  name = data_util.make_data_path(SUBREDDIT_USER_VISUALIZATION_NAME,  DataLocation.VISUALIZATION)
  logger.log("saving visualization {n}".format(n=SUBREDDIT_USER_VISUALIZATION_NAME), Level.INFO)
  vis_network.save_graph(name)

def __generate_and_visualize(config: Config, logger:Logger, token: Cancel_Token,on_done_callback: Callable):
  with token:
    logger.log("starting visualization")
    mat = dg.generate_sub_sub_adjacency_mat(config,logger,token)
    if token.is_cancel_requested():
      return
    __visualize_subreddit_subreddit(mat,config,logger,token)
    if token.is_cancel_requested():
      return
    __visualize_subreddit_user(config,logger,token)
    logger.log("visualization complete")
    on_done_callback()


def run(config: Config, logger: Logger, token: Cancel_Token, on_done_callback: Callable = lambda: None):
  thread = threading.Thread(name="visualize thread", target=__generate_and_visualize,args=(config,logger,token,on_done_callback))
  thread.start()

