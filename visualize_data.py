import threading
import graph_generator as gg
from cancel_token import Cancel_Token
import data_util
import numpy as np
import data_generator as dg
from app_config import Config
from simple_logging import Logger, Level
from pyvis.network import Network
from data_util import DataLocation
from networkx.classes.graph import Graph
from colorpallet import ColorPallet

__SUBREDDIT_SUBREDDIT_VISUALIZATION_NAME = "reddit_visualization_subreddit_subreddit.html"
__SUBREDDIT_USER_VISUALIZATION_NAME ="reddit_visualization_subreddit_user.html"



def __build_network_from_graph(graph: Graph,physics: bool, buttons_filter=[])->Network:
  vis_network = Network('1920px','1920px',bgcolor=ColorPallet.BACKGROUND_COLOR.value,font_color=ColorPallet.FONT_COLOR.value)
  vis_network.from_nx(graph)
  vis_network.force_atlas_2based()
  vis_network.toggle_physics(physics)
  vis_network.show_buttons(filter_=buttons_filter)
  return vis_network

def __visualize_subreddit_subreddit(adj_mat: np.ndarray, config: Config, logger:Logger, token: Cancel_Token):
  graph = gg.build_graph_subreddit_subreddit(adj_mat,config,logger,token)
  if token.is_cancel_requested():
    return
  vis_network = __build_network_from_graph(graph,False,['nodes', 'edges', 'layout', 'interaction', 'manipulation', 'selection', 'renderer'])

  name = data_util.make_data_path(__SUBREDDIT_SUBREDDIT_VISUALIZATION_NAME,  DataLocation.VISUALIZATION)
  logger.log("saving visualization {n}".format(n=__SUBREDDIT_SUBREDDIT_VISUALIZATION_NAME), Level.INFO)
  vis_network.save_graph(name)
  

def __visualize_subreddit_user(config: Config, logger:Logger, token: Cancel_Token):
  graph = gg.build_graph_subreddit_user(config,logger,token)

  vis_network = __build_network_from_graph(graph,True,['physics'])

  name = data_util.make_data_path(__SUBREDDIT_USER_VISUALIZATION_NAME,  DataLocation.VISUALIZATION)
  logger.log("saving visualization {n}".format(n=__SUBREDDIT_USER_VISUALIZATION_NAME), Level.INFO)
  vis_network.save_graph(name)

def __generate_and_visualize(config: Config, logger:Logger, token: Cancel_Token):
  with token:
    mat = dg.generate_sub_sub_adjacency_mat(config,logger,token)
    logger.log(str(mat),Level.INFO)
    if token.is_cancel_requested():
      return
    __visualize_subreddit_subreddit(mat,config,logger,token)
    if token.is_cancel_requested():
      return
    __visualize_subreddit_user(config,logger,token)
    logger.log("visualization complete")


def run(config: Config, logger: Logger, token: Cancel_Token):
  thread = threading.Thread(name="visualize thread", target=__generate_and_visualize,args=(config,logger,token))
  thread.start()

