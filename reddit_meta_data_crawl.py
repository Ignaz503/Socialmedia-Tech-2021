from cancel_token import Cancel_Token
import praw
from praw import Reddit
from praw.models import Subreddit
from app_config import Config
from simple_logging import Logger
from defines import CLIENT_ID, CLIENT_SECRET, USER_AGENT
from subreddit import Crawl_Metadata, Subreddit_Metadata 

def handle_subreddit(subreddit: Subreddit, meta_data: Crawl_Metadata, logger: Logger):
  name = subreddit.display_name
  sub_meta = Subreddit_Metadata(subreddit.subscribers,subreddit.public_description,subreddit.created_utc)
  meta_data.add_meta_data(name,sub_meta)

def run(crawl_metaData: Crawl_Metadata, config: Config, logger: Logger, token: Cancel_Token)-> Crawl_Metadata:
  with token:
    reddit:Reddit = praw.Reddit(
      client_id=CLIENT_ID,
      client_secret=CLIENT_SECRET,
      user_agent=USER_AGENT)
    logger.log("Crawling for subreddit metadata")
    for sub in config.subreddits_to_crawl:
      if token.is_cancel_requested():
        break
      logger.log("getting meta data for {s}".format(s=sub))
      handle_subreddit(reddit.subreddit(sub),crawl_metaData,logger)
    return crawl_metaData

  