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

def __build_network_from_graph(graph: Graph,physics: bool, buttons_filter=[])->Network:
  vis_network = Network('1920px','1920px',bgcolor=ColorPallet.BACKGROUND_COLOR.value,font_color=ColorPallet.FONT_COLOR.value)
  vis_network.from_nx(graph)
  vis_network.force_atlas_2based()
  vis_network.toggle_physics(physics)
  vis_network.show_buttons(filter_=buttons_filter)
  return vis_network

def __visualize_subreddit_subreddit(crawl_metadata: Crawl_Metadata, config: Config, logger:Logger, token: Cancel_Token, load_data_from_disk:bool):
  logger.log("viusalizing subreddit to subreddit graph")

  graph = None
  if load_data_from_disk:
    logger.log("loading data for visualization subreddit subreddit")
    graph = GraphDataFiles.SUBREDDIT_SUBREDDIT.load(config)
  else:
    logger.log("Generating data for visualization subreddit subreddit")
    mat = dg.generate_sub_sub_adjacency_mat(config,logger,token)
    graph = gg.build_graph_subreddit_subreddit(mat,crawl_metadata,config,logger,token)

  if token.is_cancel_requested():
    return
  logger.log("creating visualization")
  vis_network = __build_network_from_graph(graph,False,['nodes', 'edges', 'layout', 'interaction', 'manipulation', 'selection', 'renderer'])

  name = VisualizationDataFiles.SUBREDDIT_SUBREDDIT.get_file_path(config)
  logger.log("saving visualization {n}".format(n=VisualizationDataFiles.SUBREDDIT_SUBREDDIT.value), Level.INFO)
  vis_network.save_graph(name)
  

def __visualize_subreddit_user(users: UniqueUsers,crawl_metadata: Crawl_Metadata,config: Config, logger:Logger, token: Cancel_Token, load_data_from_disk: bool):
  logger.log("visulaizting subreddit user graph")

  graph = None
  if load_data_from_disk:
    logger.log("loading data for visualization subreddit user")
    graph = GraphDataFiles.SUBREDDIT_USER.load(config)
  else:
    logger.log("Generating data for visualization subreddit user")
    graph = gg.build_graph_subreddit_user(users,crawl_metadata,config,logger,token)

  logger.log("creating visualization")
  vis_network = __build_network_from_graph(graph,True,['physics'])

  name = VisualizationDataFiles.SUBREDDIT_USER.get_file_path(config)
  logger.log("saving visualization {n}".format(n=VisualizationDataFiles.SUBREDDIT_USER.value), Level.INFO)
  vis_network.save_graph(name)

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

    if token.is_cancel_requested():
      return
    __visualize_subreddit_subreddit(crawl_metadata,config,logger,token,load_data_from_disk)
    if token.is_cancel_requested():
      return

    users = None
    if load_data_from_disk:
      logger.log("loading unique users for visualization")
      users = UniqueUsers.load(config)
    else:
      users = data_generator.generate_unique_user(config,logger,token)

    __visualize_subreddit_user(users,crawl_metadata,config,logger,token,load_data_from_disk)
    logger.log("visualization complete")
    on_done_callback()


def run(config: Config, logger: Logger, token: Cancel_Token,load_data_from_disk: bool ,on_done_callback: Callable = lambda: None):
  thread = threading.Thread(name="visualize thread", target=__generate_and_visualize,args=(config,logger,token,load_data_from_disk,on_done_callback))
  thread.start()

