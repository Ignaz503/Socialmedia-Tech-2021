from typing import Callable
import threading
import reddit_crawl.util.helper_functions as rh
from utility.app_config import Config
from psaw import PushshiftAPI
from utility.simple_logging import Level, Logger
from utility.cancel_token import Cancel_Token
from reddit_crawl.util.context import Thread_Safe_Context
from reddit_crawl.util.diagnostics import Reddit_Crawl_Diagnostics
from reddit_crawl.data.bot_blacklist import Threadsafe_Bot_Blacklist
from reddit_crawl.data.subreddit import Subreddit_Batch_Queue, Subreddit_Batch

__LIMIT = 1000

def handle_subreddit(sub_name: str, api: PushshiftAPI, context: Thread_Safe_Context, queue: Subreddit_Batch_Queue, token: Cancel_Token):
  context.crawl_diagnostics.update_subreddit(sub_name)
  count = 0
  for submission in api.search_submissions(after= context.config.start_epoch(), before=context.config.end_epoch(),subreddit=sub_name):
    if token.is_cancel_requested():
      break
    if count > __LIMIT:
      break
    rh.handle_post_thread_safe(submission,context,token)
    count += 1

  data = None
  new_batch = Subreddit_Batch()
  with context.current_data_lock:
    data = context.current_data
    context.current_data = new_batch
  queue.enqueue(data)
  
def handle_crawl(context: Thread_Safe_Context,queue: Subreddit_Batch_Queue, token:Cancel_Token):
  api = PushshiftAPI(context.reddit)

  context.logger.log(f"crawling submissions from {context.config.from_date} to {context.config.to_date}")
  for sub in context.config.subreddits_to_crawl:
    if token.is_cancel_requested():
      break
    handle_subreddit(sub,api,context,queue,token)
  data = None
  with context.current_data_lock:
    data = context.current_data
  queue.enqueue(data)


def __execute_crawl(config: Config, logger: Logger, blacklist: Threadsafe_Bot_Blacklist, batch_queue: Subreddit_Batch_Queue, token: Cancel_Token, callback:Callable, diagnostics: Reddit_Crawl_Diagnostics):
  with  token:
    reddit = config.get_reddit_instance(logger)
    if reddit is None:
      return
    if diagnostics is None:
      diagnostics = Reddit_Crawl_Diagnostics()

    context = Thread_Safe_Context(reddit,config, Subreddit_Batch(),logger,blacklist,diagnostics)
    rh.start_batch_submit_thread("historical crawl",context,batch_queue,token)

    handle_crawl(context,batch_queue,token)
    context.crawl_diagnostics.end_timing()
    context.crawl_diagnostics.log(context.logger)
    callback()


def run(config: Config, logger: Logger, blacklist: Threadsafe_Bot_Blacklist, batch_queue: Subreddit_Batch_Queue, token: Cancel_Token, callback:Callable = lambda: None, diagnostics: Reddit_Crawl_Diagnostics = None):
  thread = threading.Thread(name="historical_crawl", daemon=True, target=__execute_crawl, args=(config,logger,blacklist,batch_queue,token,callback, diagnostics))
  thread.start()