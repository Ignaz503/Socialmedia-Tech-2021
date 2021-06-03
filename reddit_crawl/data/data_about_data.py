import  reddit_crawl.data.bot_blacklist as bot_list
from reddit_crawl.data.subreddit import Subreddit_Data
from utility.cancel_token import Cancel_Token
from utility.simple_logging import Logger
from reddit_crawl.data.users import MultiSubredditUsers, UniqueUsers
from utility.app_config import Config
import jsonpickle
import utility.data_util as data_util
from utility.data_util import DataLocation


class DataAboutData:
  __FILE_NAME = "data_about_data.json"
  number_of_subreddits: int
  number_of_unique_users: int
  number_of_bots_detected: int
  number_of_users_per_subreddit: dict[str,int]
  biggest_subreddit_by_users: tuple[list[str],int]
  smallest_subreddit_by_users: tuple[list[str],int]
  number_of_users_more_than_k_subreddits: dict[str,int]

  def __init__(self,
        num_subs:int,
        num_unique_users:int,
        num_of_bots_detected:int,
        num_users_per_sub:dict[str,int],
        biggest_sub:tuple[str,int],
        smallest_sub: tuple[str,int],
        num_users_k_subs: dict[str,int]  ) -> None:
    self.number_of_subreddits = num_subs
    self.number_of_unique_users = num_unique_users
    self.number_of_bots_detected = num_of_bots_detected
    self.number_of_users_per_subreddit = num_users_per_sub
    self.biggest_subreddit_by_users = biggest_sub
    self.smallest_subreddit_by_users  = smallest_sub
    self.number_of_users_more_than_k_subreddits = num_users_k_subs

  def to_json(self):
    return jsonpickle.encode(self,unpicklable=False,indent=2)

  def __str__(self) -> str:
      return self.to_json()

  def fill(self, unqie_users: UniqueUsers, mutli_users: MultiSubredditUsers, config: Config,logger:Logger,token: Cancel_Token):
    self.number_of_subreddits = len(config.subreddits_to_crawl)
    self.number_of_unique_users = len(unqie_users.data)

    self.number_of_bots_detected = len(bot_list.load(config.bot_list_name,config).data.blacklist)

    self.number_of_users_per_subreddit = {}
    for sub in config.subreddits_to_crawl:
      data = Subreddit_Data.load(sub,config)
      length = len(data.users)
      self.number_of_users_per_subreddit[sub] = length
      if length > self.biggest_subreddit_by_users[1]:
        self.biggest_subreddit_by_users = ([sub],length)
      elif length == self.biggest_subreddit_by_users[1]:
        self.biggest_subreddit_by_users[0].append(sub)
        
      if length < self.smallest_subreddit_by_users[1]:
        self.smallest_subreddit_by_users = ([sub],length)
      elif length == self.smallest_subreddit_by_users[1]:
        self.smallest_subreddit_by_users[0].append(sub)
    
    for i in range(1,len(config.subreddits_to_crawl)+1):
      condition = lambda _,set: len(set) > i
      count = 0
      for _ in mutli_users.iter_condition(condition):
        count+=1

      if count == 0:
        break
      entry = f"posted to more than {i}"
      self.number_of_users_more_than_k_subreddits[entry] = count

  def save_to_file(self, config: Config):
    content = self.to_json()   
    with open(data_util.make_data_path(config,DataAboutData.__FILE_NAME,DataLocation.METADATA), 'w',encoding="utf-8") as f:
      f.write(content)

  @staticmethod
  def empty():
    return DataAboutData (num_subs=0,
        num_unique_users=0,
        num_of_bots_detected=0,
        num_users_per_sub={},
        biggest_sub=([],-1),
        smallest_sub=([],2 ** 64),
        num_users_k_subs={})
