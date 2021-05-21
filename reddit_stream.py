import praw
import threading
import reddit_helper as rh
from typing import Callable
from app_config import Config
from praw.reddit import Reddit
from simple_logging import Logger
from cancel_token import Cancel_Token
from context import Thread_Safe_Context
from praw.models import SubredditHelper
from diagnostics import Reddit_Crawl_Diagnostics
from bot_blacklist import Threadsafe_Bot_Blacklist
from defines import CLIENT_ID, CLIENT_SECRET, USER_AGENT
from subreddit import Subreddit_Batch_Queue, Subreddit_Batch

def __stream_monitor(monitor_type: str, stream_gen, data_handler, subs: SubredditHelper, reddit: Reddit, context: Thread_Safe_Context, queue: Subreddit_Batch_Queue, token: Cancel_Token):
  with token:
    rh.start_batch_submit_thread(monitor_type,context,queue)
    #pause after one repsone with nothing new to check if canceled, set to 0 for no delay
    context.logger.log("Start monitioring {mt} for subreddits {subs}".format(mt = monitor_type, subs = context.config.subreddits_to_crawl))
    for data in stream_gen(pause_after=1):
      if token.is_cancel_requested():
        context.logger.log("Terminating due to cancel request")
        break
      if data is None: 
        continue
      data_handler(data,context,token)
    queue.enqueue(context.current_data)
    context.logger.log("Stop monitoring of comments stream")


def __comments_stream(subs: SubredditHelper, reddit: Reddit, context: Thread_Safe_Context, queue: Subreddit_Batch_Queue, token: Cancel_Token):
  __stream_monitor("comments stream",subs.stream.comments,rh.handle_comment_thread_safe,subs,reddit,context,queue,token)
  
def __submission_stream(subs: SubredditHelper,reddit: Reddit, context: Thread_Safe_Context, queue: Subreddit_Batch_Queue, token: Cancel_Token):
  __stream_monitor("submissions stream",subs.stream.submissions,rh.handle_post_thread_safe,subs,reddit,context,queue,token)
  

def __create_stream_monitor_thread(thread_name: str, target: Callable[[SubredditHelper,Reddit,Thread_Safe_Context,Subreddit_Batch_Queue,Cancel_Token],None],config: Config, logger:Logger, blacklist: Threadsafe_Bot_Blacklist, queue: Subreddit_Batch_Queue, token: Cancel_Token):
  reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT)
  context = Thread_Safe_Context(reddit,config, Subreddit_Batch(),logger,blacklist, Reddit_Crawl_Diagnostics())

  subs_to_observe = rh.join_subreddits(config.subreddits_to_crawl)
  subs: SubredditHelper = reddit.subreddit(subs_to_observe)
  thread = threading.Thread(name=thread_name,target=target,args=(subs, reddit,context, queue, token))
  thread.start()

def __create_comments_monitor_thread(config: Config, logger:Logger, blacklist: Threadsafe_Bot_Blacklist, queue: Subreddit_Batch_Queue, token: Cancel_Token):
  return __create_stream_monitor_thread("comments_stream",__comments_stream, config, logger, blacklist, queue, token)
  
def __create_submission_monitor_thread(config: Config, logger:Logger, blacklist: Threadsafe_Bot_Blacklist, queue: Subreddit_Batch_Queue, token: Cancel_Token):
  return __create_stream_monitor_thread("submission_stream",__submission_stream,config,logger,blacklist,queue, token)

def run(config: Config, logger:Logger, blacklist: Threadsafe_Bot_Blacklist, queue: Subreddit_Batch_Queue, token: Cancel_Token):
  comments_token = __create_comments_monitor_thread(config,logger,blacklist,queue,token)
  submission_token = __create_submission_monitor_thread(config,logger,blacklist,queue,token)
  return (comments_token,submission_token)
    
