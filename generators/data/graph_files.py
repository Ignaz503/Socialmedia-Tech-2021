from enum import Enum
from utility.app_config import Config
from networkx import Graph
from utility.data_util import DataLocation
import utility.data_util as data_util
import pygraphviz
import networkx.drawing.nx_agraph as nx_agraph

class GraphDataFiles(Enum):
  SUBREDDIT_SUBREDDIT ="subreddit_subreddit.dot"
  SUBREDDIT_USER = "subreddit_user.dot"
  USER_USER_MORE_THAN_ONE = "user_user_gt1.dot"

  def get_file_path(self, config:Config):
    return data_util.make_data_path(config,self.value,DataLocation.GRAPHS)

  def load(self,config:Config) -> Graph:
    g: Graph = nx_agraph.from_agraph(pygraphviz.AGraph(filename=self.get_file_path(config)))

    for node in g.nodes(data=True):
      if 'size' in node[1]:
        node[1]['size'] = float(node[1]['size'])

    for edge in g.edges(data=True):
      if 'weight' in edge[2]:
        edge[2]['weight'] = int(edge[2]['weight'])
      if 'width' in edge[2]:
        edge[2]['width'] = float(edge[2]['width'])
    return g

  @staticmethod
  def from_name(name:str):
    for t in GraphDataFiles:
      if t.name == name:
        return t
    raise ValueError(f"{name} is not a valid VisualizationDataFiles name")
