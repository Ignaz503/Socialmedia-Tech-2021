import threading
from utility.cancel_token import Cancel_Token
from praw.models import Subreddit
from utility.app_config import Config
from utility.simple_logging import Logger, Level
from reddit_crawl.data.subreddit import Crawl_Metadata, Subreddit_Metadata 

def handle_subreddit(subreddit: Subreddit, meta_data: Crawl_Metadata, logger: Logger):
  name = subreddit.display_name
  sub_meta = Subreddit_Metadata(subreddit.subscribers,subreddit.public_description,subreddit.created_utc)
  meta_data.add_meta_data(name,sub_meta)

def __handle_crawl(crawl_metaData: Crawl_Metadata, config: Config, logger: Logger, token: Cancel_Token)-> Crawl_Metadata:
  reddit = config.get_reddit_instance(logger)
  if reddit is None:
    return
  logger.log("Crawling for subreddit metadata",Level.INFO)
  for sub in config.subreddits_to_crawl:
    if token.is_cancel_requested():
      break
    logger.log("getting meta data for {s}".format(s=sub),Level.INFO)
    handle_subreddit(reddit.subreddit(sub),crawl_metaData,logger)
  return crawl_metaData

def run_same_thread(crawl_metaData: Crawl_Metadata, config: Config, logger: Logger, token: Cancel_Token)-> Crawl_Metadata:
  __handle_crawl(crawl_metaData,config,logger,token)

def __execute(crawl_metaData: Crawl_Metadata, config: Config, logger: Logger, token: Cancel_Token):
  with token:
    __handle_crawl(crawl_metaData,config,logger,token)

def run(crawl_metaData: Crawl_Metadata, config: Config, logger: Logger, token: Cancel_Token):
  thread = threading.Thread(name="meta data crawl",target=__execute,args=(crawl_metaData,config,logger,token))
  thread.start()