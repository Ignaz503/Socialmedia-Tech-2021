import networkx as nx
from networkx.algorithms.bipartite.basic import color
from networkx.convert import to_edgelist
from pyvis.physics import Physics
from reddit_crawl.data.users import MultiSubredditUsers, UniqueUsers
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

def __get_graph_subreddit_subreddit(mat,crawl_metadata: Crawl_Metadata,config:Config,logger:Logger,token: Cancel_Token, load_data_from_disk: bool)->Graph:
  if load_data_from_disk:
    logger.log("loading data for visualization subreddit subreddit")
    return GraphDataFiles.SUBREDDIT_SUBREDDIT.load(config)
  else:
    logger.log("Generating data for visualization subreddit subreddit")
    return gg.build_graph_subreddit_subreddit(mat,crawl_metadata,config,logger,token)

def __get_graph_user_user(multi_sub_users:MultiSubredditUsers,config: Config,logger: Logger, token: Cancel_Token,load_data_from_disk:bool) -> Graph:
  if load_data_from_disk:
    logger.log("loading data for visualization subreddit user")
    return GraphDataFiles.USER_USER.load(config)
  else:
    logger.log("Generating data for visualization subreddit user")
    return gg.build_graph_user_user(multi_sub_users,config,logger,token)

def __get_graph_subreddit_user(users:UniqueUsers,crawl_metadata: Crawl_Metadata,config: Config,logger: Logger, token: Cancel_Token,load_data_from_disk:bool) -> Graph:
  if load_data_from_disk:
    logger.log("loading data for visualization subreddit user")
    return GraphDataFiles.SUBREDDIT_USER.load(config)
  else:
    logger.log("Generating data for visualization subreddit user")
    return gg.build_graph_subreddit_user(users,crawl_metadata,config,logger,token)

def __visualize_graph(graph: Graph,file:VisualizationDataFiles,config: Config, logger:Logger, token: Cancel_Token,physics=False,buttons_filter=[]):
  logger.log(f"visulaizting graph {file.name}")

  logger.log("creating visualization")
  vis_network = __build_network_from_graph(graph,physics,buttons_filter)

  name = file.get_file_path(config)
  logger.log("saving visualization {n}".format(n=file.value), Level.INFO)
  vis_network.save_graph(name)

def __color_graph_clustering(graph:Graph,gradient:ColorGradient,config: Config, logger:Logger, token: Cancel_Token):
  clustering = nx.clustering(graph)
  for c in clustering:
    if token.is_cancel_requested():
      return
    graph.nodes[c]['color'] = gradient[clustering[c]].get_hex_l()

def __generate_and_visualize(config: Config, logger:Logger, token: Cancel_Token,load_data_from_disk: bool,on_done_callback: Callable):
  with token:
    logger.log("starting visualization")

    crawl_metadata = None
    mat = None
    multi_sub_users = None
    if load_data_from_disk:
      logger.log("loading metadata for visualization")
      crawl_metadata = Crawl_Metadata.load(config)
      #mat can stay none cause we don't load from mat data we load from dot file
      multi_sub_user = MultiSubredditUsers.load(config)
    else:
      logger.log("crawling for metadata before visualization")
      crawl_metadata = Crawl_Metadata.empty()
      metadata_crawl.run_same_thread(crawl_metadata,config,logger, token)
      mat,multi_sub_user = dg.generate_sub_sub_mat_and_multi_sub_user_metadata(config,logger,token)

    #we only ever change the color so just reuse this graph
    graph = __get_graph_subreddit_subreddit(mat,crawl_metadata,config,logger,token,load_data_from_disk)

    if token.is_cancel_requested():
      return
    __visualize_graph(graph,VisualizationDataFiles.SUBREDDIT_SUBREDDIT,config,logger,token)
    if token.is_cancel_requested():
      return


    gradient = ColorGradient(Color('red'),Color('lime'),100,True)
    __color_graph_clustering(graph,gradient,config,logger,token)
    __visualize_graph(graph,VisualizationDataFiles.SUBBREDDIT_SUBBREDIT_COLORING_CLUSTER,config,logger,token)

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
    graph = __get_graph_user_user(multi_sub_users,config,logger,token,load_data_from_disk)
    __visualize_graph(graph,VisualizationDataFiles.USER_USER,config,logger,token,physics=True,buttons_filter=['physics'])

    logger.log("visualization complete")
    on_done_callback()


def run(config: Config, logger: Logger, token: Cancel_Token,load_data_from_disk: bool ,on_done_callback: Callable = lambda: None):
  thread = threading.Thread(name="visualize thread", target=__generate_and_visualize,args=(config,logger,token,load_data_from_disk,on_done_callback))
  thread.start()

