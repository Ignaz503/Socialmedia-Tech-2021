import networkx as nx
import networkx.algorithms.centrality as nx_centrality
import networkx.algorithms.bridges as nx_bridge
from networkx.algorithms.centrality import harmonic
from networkx.readwrite.gml import Token
from reddit_crawl.data.users import MultiSubredditUsers, UniqueUsers
from reddit_crawl.data.subreddit import Crawl_Metadata
import threading
from typing import Any, Callable
import generators.graph_generator as gg
from utility.cancel_token import Cancel_Token
import generators.util as dg
from utility.app_config import Config
from utility.simple_logging import Logger, Level
from pyvis.network import Network
from networkx.classes.graph import Graph
from utility.colorpallet import ColorPallet, DefaultColorPallet
from generators.data.visualization_files import VisualizationDataFile
from generators.data.graph_files import GraphDataFiles
import reddit_crawl.meta_data_crawl as metadata_crawl
import generators.data_generator as data_generator
from utility.color import ColorGradient
from colour import Color
import math

__SUBREDDIT_SUBREDDIT = "subreddit_subreddit.html"
__SUBBREDDIT_SUBBREDIT_COLORING_CLUSTER = "subreddit_subreddit_coloring_cluster.html"
__SUBREDDIT_USER = "subreddit_user.html"
__USER_USER_MORE_THAN_ONE = "user_user_gt1.html"

def __build_network_from_graph(graph: Graph,physics: bool, buttons_filter=[])->Network:
  vis_network = Network('1920px','1920px',bgcolor=DefaultColorPallet.BACKGROUND_COLOR.value,font_color=DefaultColorPallet.FONT_COLOR.value)
  vis_network.from_nx(graph)
  vis_network.force_atlas_2based(gravity=-200,spring_length=315,overlap=1)
  #vis_network.hrepulsion(node_distance=250)
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

def __get_graph_user_user(multi_sub_users:MultiSubredditUsers,file: GraphDataFiles,config: Config,logger: Logger, token: Cancel_Token,load_data_from_disk:bool) -> Graph:
  if load_data_from_disk:
    logger.log("loading data for visualization subreddit user")
    return file.load(config)
  else:
    logger.log("Generating data for visualization subreddit user")
    if file is GraphDataFiles.USER_USER_MORE_THAN_ONE:
      return gg.build_graph_user_user(multi_sub_users,2,config,logger,token)
    else:
      return gg.build_graph_user_user(multi_sub_users,1,config,logger,token)

def __get_graph_subreddit_user(users:UniqueUsers,crawl_metadata: Crawl_Metadata,config: Config,logger: Logger, token: Cancel_Token,load_data_from_disk:bool) -> Graph:
  if load_data_from_disk:
    logger.log("loading data for visualization subreddit user")
    return GraphDataFiles.SUBREDDIT_USER.load(config)
  else:
    logger.log("Generating data for visualization subreddit user")
    return gg.build_graph_subreddit_user(users,crawl_metadata,config,logger,token)

def __visualize_graph(graph: Graph,file:VisualizationDataFile,config: Config, logger:Logger, token: Cancel_Token,physics=True,buttons_filter=['physics','interaction']):
  logger.log(f"visulaizting graph {file.name}")

  logger.log("creating visualization")
  vis_network = __build_network_from_graph(graph,physics,buttons_filter)

  path = file.get_file_path(config)
  logger.log("saving visualization {n} to  {l}".format(n=file.name,l=path), Level.INFO)
  vis_network.save_graph(path)

def __color_graph_clustering(graph:Graph,gradient:ColorGradient,logger:Logger, token: Cancel_Token):
  clustering = nx.clustering(graph)
  for c in clustering:
    if token.is_cancel_requested():
      return
    graph.nodes[c]['color'] = gradient[clustering[c]].get_hex_l()

def __color_graph_edges(graph:Graph,color_hex_code:str):
  for edge in graph.edges(data=True):
    edge[2]['color'] = color_hex_code

def __color_graph_nodes(graph:Graph, color_hex_code:str):
  for node in graph.nodes(data=True):
    node[1]['color']= color_hex_code


def __color_graph_centrality(graph: Graph,gradient:ColorGradient, centrality_func: Callable[[Graph],dict[int,Any]], logger:Logger,token: Cancel_Token):
    #v-min / max
    cent_dict = centrality_func(graph)

    min = float("inf")
    max = float("-inf")

    for node in cent_dict:
      if cent_dict[node]> max:
        max = cent_dict[node]
      if cent_dict[node]<min:
        min =cent_dict[node]

    if math.isclose(max,0):
      max = 0.0001

    if max == min:
      max += 0.0001

    for node in cent_dict:
      t = (cent_dict[node]-min)/(max-min)  
      col = gradient.get(t)
      graph.nodes[node]['color'] = col.get_hex_l()

def __visualize_centrality(graph: Graph, cent_func: Callable[[Graph],dict[int,Any]],name:str,gradient: ColorGradient,config: Config,logger: Logger,token: Cancel_Token):
  __color_graph_centrality(graph,gradient,cent_func,logger,token)
  __visualize_graph(graph, VisualizationDataFile(name),config,logger,token)

def __color_bridges(graph: Graph,color:Color,config: Config,logger:Logger, token: Cancel_Token):
  hex_code = color.get_hex_l()
  for bridge in nx_bridge(graph):
    graph.edges[bridge]['color'] = hex_code

def __viusalize_centraliteis(graph: Graph,name_base:str,gradient: ColorGradient, config: Config, logger: Logger, token: Cancel_Token):
  __visualize_centrality(graph,nx_centrality.degree_centrality,name_base+"_coloring_deg_cent.html",gradient,config,logger,token)
  __visualize_centrality(graph,nx_centrality.eigenvector_centrality,name_base+"_coloring_egien_cent.html",gradient,config,logger,token)
  __visualize_centrality(graph,nx_centrality.harmonic_centrality,name_base+":coloring_harmonic_cent.html",gradient,config,logger,token)
  __visualize_centrality(graph,nx_centrality.subgraph_centrality,name_base+"_coloring_sub_graph_cent.html",gradient,config,logger,token)
  __visualize_centrality(graph,nx_centrality.betweenness_centrality,name_base+"_coloring_betweenness.html",gradient,config,logger,token)
  if nx.is_connected(graph):
    __visualize_centrality(graph,nx_centrality.current_flow_closeness_centrality,name_base+"_coloring_current_flow_cent.html",gradient,config,logger,token)
  __visualize_centrality(graph,nx_centrality.closeness_centrality,name_base+"_coloring_closeness_cent.html",gradient,config,logger,token)

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
      multi_sub_users = MultiSubredditUsers.load(config)
    else:
      logger.log("crawling for metadata before visualization")
      crawl_metadata = Crawl_Metadata.empty()
      metadata_crawl.run_same_thread(crawl_metadata,config,logger, token)
      mat,multi_sub_users = dg.generate_sub_sub_mat_and_multi_sub_user_metadata(config,logger,token)

    #we only ever change the color so just reuse this graph
    graph = __get_graph_subreddit_subreddit(mat,crawl_metadata,config,logger,token,load_data_from_disk)

    if token.is_cancel_requested():
      return
    __visualize_graph(graph,VisualizationDataFile(__SUBREDDIT_SUBREDDIT),config,logger,token)
    if token.is_cancel_requested():
      return

    gradient = ColorGradient(Color('red'),Color('lime'),100,True)
    __color_graph_clustering(graph,gradient,logger,token)
    __visualize_graph(graph,VisualizationDataFile(__SUBBREDDIT_SUBBREDIT_COLORING_CLUSTER),config,logger,token)
    __viusalize_centraliteis(graph,"subreddit_subreddit",gradient, config, logger, token)

    __color_graph_nodes(graph,DefaultColorPallet.SUBREDDIT_COLOR.value)
    __color_bridges(graph,Color("#b2e945"),config,logger,token)
    __visualize_graph(graph,VisualizationDataFile("subreddit_subreddit_coloring_bridges.html"),config,logger,token)

    users = None
    if load_data_from_disk:
      logger.log("loading unique users for visualization")
      users = UniqueUsers.load(config)
    else:
      users = data_generator.generate_unique_user(config,logger,token)

    graph = __get_graph_subreddit_user(users,crawl_metadata,config, logger, token, load_data_from_disk)

    __visualize_graph(graph,VisualizationDataFile(__SUBREDDIT_USER),config,logger,token)
    
    gg.modify_graph_remove_degree_less_than(graph,2)
    __visualize_graph(graph,VisualizationDataFile("subreddit_user_simple.html"),config,logger,token)
    __viusalize_centraliteis(graph,"subreddit_user_simple",gradient, config, logger, token)

    if token.is_cancel_requested():
      return
    #todo
    graph = __get_graph_user_user(multi_sub_users,GraphDataFiles.USER_USER_MORE_THAN_ONE,config,logger,token,load_data_from_disk)
    __visualize_graph(graph,VisualizationDataFile(__USER_USER_MORE_THAN_ONE),config,logger,token)
    
    __viusalize_centraliteis(graph,"user_user_gt1_col_edge_",gradient, config, logger, token)
    
    __color_graph_edges(graph,DefaultColorPallet.EDGE_COLOR.value[0])
    __viusalize_centraliteis(graph,"user_user_gt1",gradient, config, logger, token)


    logger.log("visualization complete")
    on_done_callback()

def run(config: Config, logger: Logger, token: Cancel_Token,load_data_from_disk: bool ,on_done_callback: Callable = lambda: None):
  thread = threading.Thread(name="visualize thread", target=__generate_and_visualize,args=(config,logger,token,load_data_from_disk,on_done_callback))
  thread.start()
