import threading
import reddit_crawl.util.helper_functions as rh
from typing import Callable
from utility.app_config import Config
from praw.reddit import Reddit
from utility.simple_logging import Logger, Level
from utility.cancel_token import Cancel_Token
from reddit_crawl.util.context import Thread_Safe_Context
from praw.models import SubredditHelper
from reddit_crawl.util.diagnostics import Reddit_Crawl_Diagnostics
from reddit_crawl.data.bot_blacklist import Threadsafe_Bot_Blacklist
from reddit_crawl.data.subreddit import Subreddit_Batch_Queue, Subreddit_Batch

def __stream_monitor(monitor_type: str, stream_gen, data_handler, subs: SubredditHelper, reddit: Reddit, context: Thread_Safe_Context, queue: Subreddit_Batch_Queue, token: Cancel_Token):
  rh.start_batch_submit_thread(monitor_type,context,queue)
  #pause after one repsone with nothing new to check if canceled, set to 0 for no delay
  context.logger.log("Start monitioring {mt} for subreddits {subs}".format(mt = monitor_type, subs = context.config.subreddits_to_crawl),Level.INFO)
  for data in stream_gen(pause_after=1):
    if token.is_cancel_requested():
      context.logger.log("Terminating due to cancel request",Level.INFO)
      break
    if data is None: 
      context.crawl_diagnostics.update_timing()
      continue
    data_handler(data,context,token)
  queue.enqueue(context.current_data)
  context.crawl_diagnostics.end_timing()
  context.logger.log(f"Stop monitoring of {monitor_type}",Level.INFO)


def __comments_stream(config: Config, logger:Logger, blacklist: Threadsafe_Bot_Blacklist, queue: Subreddit_Batch_Queue, token: Cancel_Token, diagnostics: Reddit_Crawl_Diagnostics):
  with token:
    reddit = config.get_reddit_instance(logger)
    if reddit is None:
      return
    if diagnostics is None:
      diagnostics = Reddit_Crawl_Diagnostics()

    context = Thread_Safe_Context(reddit,config, Subreddit_Batch(),logger,blacklist, diagnostics)

    subs_to_observe = rh.join_subreddits(config.subreddits_to_crawl)
    subs: SubredditHelper = reddit.subreddit(subs_to_observe)
    __stream_monitor("comments stream",subs.stream.comments,rh.handle_comment_thread_safe,subs,reddit,context,queue,token)
  
def __submission_stream(config: Config, logger:Logger, blacklist: Threadsafe_Bot_Blacklist, queue: Subreddit_Batch_Queue, token: Cancel_Token, diagnostics: Reddit_Crawl_Diagnostics):
  with token:
    reddit = config.get_reddit_instance(logger)
    if reddit is None:
      return
    if diagnostics is None:
      diagnostics = Reddit_Crawl_Diagnostics()

    context = Thread_Safe_Context(reddit,config, Subreddit_Batch(),logger,blacklist, diagnostics)

    subs_to_observe = rh.join_subreddits(config.subreddits_to_crawl)
    subs: SubredditHelper = reddit.subreddit(subs_to_observe)
    __stream_monitor("submissions stream",subs.stream.submissions,rh.handle_post_thread_safe,subs,reddit,context,queue,token)
  

def __create_stream_monitor_thread(thread_name: str,
     target: Callable[[SubredditHelper,Reddit,Thread_Safe_Context,Subreddit_Batch_Queue,Cancel_Token],None],
     config: Config,
     logger:Logger, 
     blacklist: Threadsafe_Bot_Blacklist,
     queue: Subreddit_Batch_Queue,
     token: Cancel_Token,
     diagnostics: Reddit_Crawl_Diagnostics):
  thread = threading.Thread(name=thread_name,target=target,args=(config, logger, blacklist, queue, token,diagnostics))
  thread.start()

def __create_comments_monitor_thread(config: Config,
     logger:Logger,
     blacklist: Threadsafe_Bot_Blacklist,
     queue: Subreddit_Batch_Queue,
     token: Cancel_Token,
     diagnostics: Reddit_Crawl_Diagnostics):
  return __create_stream_monitor_thread("comments_stream",__comments_stream, config, logger, blacklist, queue, token,diagnostics)
  
def __create_submission_monitor_thread(config: Config,
    logger:Logger,
    blacklist: Threadsafe_Bot_Blacklist,
    queue: Subreddit_Batch_Queue,
    token: Cancel_Token,
    diagnostics: Reddit_Crawl_Diagnostics):
  return __create_stream_monitor_thread("submission_stream",__submission_stream,config,logger,blacklist,queue, token,diagnostics)

def run(config: Config,
    logger:Logger,
    blacklist: Threadsafe_Bot_Blacklist,
    queue: Subreddit_Batch_Queue,
    token: Cancel_Token,
    diagnostics_comments:Reddit_Crawl_Diagnostics = None,
    diagnostics_submissions:Reddit_Crawl_Diagnostics = None):
  comments_token = __create_comments_monitor_thread(config,logger,blacklist,queue,token,diagnostics_comments)
  submission_token = __create_submission_monitor_thread(config,logger,blacklist,queue,token,diagnostics_submissions)
  return (comments_token,submission_token)
    
