from typing import Callable
import praw
import threading
import reddit_crawl.util.helper_functions as rh
from utility.app_config import Config
from psaw import PushshiftAPI
from utility.simple_logging import Logger
from utility.cancel_token import Cancel_Token
from reddit_crawl.util.context import Thread_Safe_Context
from reddit_crawl.util.diagnostics import Reddit_Crawl_Diagnostics
from reddit_crawl.data.bot_blacklist import Threadsafe_Bot_Blacklist
from defines import CLIENT_ID, CLIENT_SECRET, USER_AGENT
from reddit_crawl.data.subreddit import Subreddit_Batch_Queue, Subreddit_Batch

def handle_subreddit(sub_name: str, api: PushshiftAPI, context: Thread_Safe_Context, queue: Subreddit_Batch_Queue, token: Cancel_Token):
  for submission in api.search_submissions(after= context.config.start_epoch(), before=context.config.end_epoch(),subreddit=sub_name):
    if token.is_cancel_requested():
      break
    rh.handle_post_thread_safe(submission,context,token)

  data = None
  new_batch = Subreddit_Batch()
  with context.current_data_lock:
    data = context.current_data
    context.current_data = new_batch
  queue.enqueue(data)
  
def handle_crawl(context: Thread_Safe_Context,queue: Subreddit_Batch_Queue, token:Cancel_Token):
  api = PushshiftAPI(context.reddit)

  for sub in context.config.subreddits_to_crawl:
    if token.is_cancel_requested():
      break
    handle_subreddit(sub,api,context,queue,token)
  data = None
  with context.current_data_lock:
    data = context.current_data
  queue.enqueue(data)


def __execute_crawl(config: Config, logger: Logger, blacklist: Threadsafe_Bot_Blacklist, batch_queue: Subreddit_Batch_Queue, token: Cancel_Token, callback:Callable):
  with  token:
    reddit = praw.Reddit(
      client_id=config.reddit_app_info[CLIENT_ID],
      client_secret=config.reddit_app_info[CLIENT_SECRET],
      user_agent=config.reddit_app_info[USER_AGENT])

    context = Thread_Safe_Context(reddit,config, Subreddit_Batch(),logger,blacklist, Reddit_Crawl_Diagnostics())
    rh.start_batch_submit_thread("historical crawl",context,batch_queue)

    handle_crawl(context,batch_queue,token)
    context.crawl_diagnostics.end_timing()
    context.crawl_diagnostics.log(context.logger)
    callback()


def run(config: Config, logger: Logger, blacklist: Threadsafe_Bot_Blacklist, batch_queue: Subreddit_Batch_Queue, token: Cancel_Token, callback:Callable = lambda: None):
  thread = threading.Thread(name="historical_crawl", daemon=True, target=__execute_crawl, args=(config,logger,blacklist,batch_queue,token,callback))
  thread.start()