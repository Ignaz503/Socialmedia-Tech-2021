import networkx as nx
from networkx.algorithms.bipartite.basic import color
from networkx.convert import to_edgelist
from pyvis.physics import Physics
from reddit_crawl.data.users import UniqueUsers
from reddit_crawl.data.subreddit import Crawl_Metadata
import threading
from typing import Callable
import generators.graph_generator as gg
from utility.cancel_token import Cancel_Token
import generators.util as dg
from utility.app_config import Config
from utility.simple_logging import Logger, Level
from pyvis.network import Network
from networkx.classes.graph import Graph
from utility.colorpallet import ColorPallet
from generators.data.visualization_files import VisualizationDataFiles
from generators.data.graph_files import GraphDataFiles
import reddit_crawl.meta_data_crawl as metadata_crawl
import generators.data_generator as data_generator
from utility.color import ColorGradient
from colour import Color

def __build_network_from_graph(graph: Graph,physics: bool, buttons_filter=[])->Network:
  vis_network = Network('1920px','1920px',bgcolor=ColorPallet.BACKGROUND_COLOR.value,font_color=ColorPallet.FONT_COLOR.value)
  vis_network.from_nx(graph)
  vis_network.force_atlas_2based()
  vis_network.toggle_physics(physics)
  vis_network.show_buttons(filter_=buttons_filter)
  return vis_network

def __get_graph_subreddit_subreddit(crawl_metadata: Crawl_Metadata,config:Config,logger:Logger,token: Cancel_Token, load_data_from_disk: bool):
  graph = None
  if load_data_from_disk:
    logger.log("loading data for visualization subreddit subreddit")
    graph = GraphDataFiles.SUBREDDIT_SUBREDDIT.load(config)
  else:
    logger.log("Generating data for visualization subreddit subreddit")
    mat = dg.generate_sub_sub_adjacency_mat(config,logger,token)
    graph = gg.build_graph_subreddit_subreddit(mat,crawl_metadata,config,logger,token)
  return graph
  
def __get_graph_user_user(users:UniqueUsers,config: Config,logger: Logger, token: Cancel_Token,load_data_from_disk:bool) -> Graph:
  graph = None
  if load_data_from_disk:
    logger.log("loading data for visualization subreddit user")
    graph = GraphDataFiles.USER_USER.load(config)
  else:
    logger.log("Generating data for visualization subreddit user")
    graph = gg.build_graph_user_user(users,config,logger,token)
  return graph

def __get_graph_subreddit_user(users:UniqueUsers,crawl_metadata: Crawl_Metadata,config: Config,logger: Logger, token: Cancel_Token,load_data_from_disk:bool) -> Graph:
  graph = None
  if load_data_from_disk:
    logger.log("loading data for visualization subreddit user")
    graph = GraphDataFiles.SUBREDDIT_USER.load(config)
  else:
    logger.log("Generating data for visualization subreddit user")
    graph = gg.build_graph_subreddit_user(users,crawl_metadata,config,logger,token)
  return graph

def __visualize_graph(graph: Graph,file:VisualizationDataFiles,config: Config, logger:Logger, token: Cancel_Token,physics=False,buttons_filter=[]):
  logger.log(f"visulaizting graph {file.name}")

  logger.log("creating visualization")
  vis_network = __build_network_from_graph(graph,physics,buttons_filter)

  name = file.get_file_path(config)
  logger.log("saving visualization {n}".format(n=file.value), Level.INFO)
  vis_network.save_graph(name)

def __visualize_subbreddit_subreddit_coloring_cluster(graph:Graph,config: Config, logger:Logger, token: Cancel_Token, load_data_from_disk: bool):
  gradient = ColorGradient(Color('red'),Color('lime'),100,True)

  clustering = nx.clustering(graph)
  for c in clustering:
    graph.nodes[c]['color'] = gradient[clustering[c]].get_hex_l()

  __visualize_graph(graph,VisualizationDataFiles.SUBBREDDIT_SUBBREDIT_COLORING_CLUSTER,config,logger,token)


def __generate_and_visualize(config: Config, logger:Logger, token: Cancel_Token,load_data_from_disk: bool,on_done_callback: Callable):
  with token:
    logger.log("starting visualization")

    crawl_metadata = None
    if load_data_from_disk:
      logger.log("loading metadata for visualization")
      crawl_metadata = Crawl_Metadata.load(config)
    else:
      logger.log("crawling for metadata before visualization")
      crawl_metadata = Crawl_Metadata.empty()
      metadata_crawl.run_same_thread(crawl_metadata,config,logger, token)

    #we only ever change the color so just reuse this graph
    graph = __get_graph_subreddit_subreddit(crawl_metadata,config,logger,token,load_data_from_disk)

    if token.is_cancel_requested():
      return
    __visualize_graph(graph,VisualizationDataFiles.SUBREDDIT_SUBREDDIT,config,logger,token)
    if token.is_cancel_requested():
      return

    __visualize_subbreddit_subreddit_coloring_cluster(
      graph,
      config,
      logger,
      token,
      load_data_from_disk=True)#prev vis generated the data

    users = None
    if load_data_from_disk:
      logger.log("loading unique users for visualization")
      users = UniqueUsers.load(config)
    else:
      users = data_generator.generate_unique_user(config,logger,token)

    graph = __get_graph_subreddit_user(users,crawl_metadata,config, logger, token, load_data_from_disk)

    __visualize_graph(graph,VisualizationDataFiles.SUBREDDIT_USER,config,logger,token)
    if token.is_cancel_requested():
      return
    #todo
    graph = __get_graph_user_user(users,config,logger,token,load_data_from_disk)
    __visualize_graph(graph,VisualizationDataFiles.USER_USER,config,logger,token,physics=True,buttons_filter=['physics'])

    logger.log("visualization complete")
    on_done_callback()


def run(config: Config, logger: Logger, token: Cancel_Token,load_data_from_disk: bool ,on_done_callback: Callable = lambda: None):
  thread = threading.Thread(name="visualize thread", target=__generate_and_visualize,args=(config,logger,token,load_data_from_disk,on_done_callback))
  thread.start()

