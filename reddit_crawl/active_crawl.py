import time
import threading
import traceback
import reddit_crawl.util.helper_functions as rh
from reddit_crawl.util.context import Thread_Safe_Context
from utility.app_config import Config
from utility.simple_logging import Logger, Level
from utility.cancel_token import Cancel_Token
from praw.models import Comment, Submission
from reddit_crawl.util.diagnostics import Reddit_Crawl_Diagnostics
from reddit_crawl.data.bot_blacklist import Threadsafe_Bot_Blacklist
from reddit_crawl.data.subreddit import Subreddit_Batch_Queue, Subreddit_Batch
from defines import MIN_REPEAT_TIME

def __handle_crawl(context: Thread_Safe_Context,batch_queue: Subreddit_Batch_Queue, token: Cancel_Token):
  for sub in context.config.subreddits_to_crawl:
    if token.is_cancel_requested():
      break
    subreddit = context.reddit.subreddit(sub)
    context.crawl_diagnostics.update_subreddit(subreddit.display_name)
    context.logger.log("Crawling subreddits: {subreddit}".format(subreddit = sub),Level.INFO)
    try:
      for submission in context.config.get_submission_getter().get(subreddit,context.config.number_of_posts, context.logger):
        if token.is_cancel_requested():
          break
        rh.handle_post_thread_safe(submission, context, token)
    except Exception as err:
      print(err)
      traceback.print_tb(err.__traceback__)
    batch_queue.enqueue(context.current_data)
    context.current_data = Subreddit_Batch()

def __execute_crawl(config: Config, logger: Logger, blacklist: Threadsafe_Bot_Blacklist, batch_queue: Subreddit_Batch_Queue,token: Cancel_Token, wait_period_seconds: float, only_once: bool,diagnostics: Reddit_Crawl_Diagnostics):
  with token:
    reddit = config.get_reddit_instance(logger)
    if reddit is None:
      return
    if diagnostics is None:
      diagnostics = Reddit_Crawl_Diagnostics()

    context = Thread_Safe_Context(reddit,config, Subreddit_Batch(),logger,blacklist, diagnostics)
    rh.start_batch_submit_thread("active crawl batch submit",context,batch_queue,token)
    logger.log("executing crawl every {s} seconds".format(s = wait_period_seconds),Level.INFO)

    current_time = time.perf_counter()
    last_execution = float('-inf') # start running
    
    while not token.is_cancel_requested():
      if current_time - last_execution >= wait_period_seconds:
        last_execution = current_time
        __handle_crawl(context, batch_queue, token)
        batch_queue.enqueue(context.current_data)
        context.crawl_diagnostics.end_timing()
        context.crawl_diagnostics.log(context.logger)
        context.crawl_diagnostics.reset_timing()
      if only_once:
        break
      current_time = time.perf_counter()
    batch_queue.enqueue(context.current_data)
    logger.log("active crawl stopped")



def run(config: Config, logger: Logger, blacklist: Threadsafe_Bot_Blacklist, batch_queue: Subreddit_Batch_Queue, token: Cancel_Token, diagnostics: Reddit_Crawl_Diagnostics = None):
  seconds = config.get_repeat_time_in_seconds()
  only_once = False
  if seconds == 0:
    only_once = True

  if seconds < MIN_REPEAT_TIME:
    seconds = MIN_REPEAT_TIME

  thread = threading.Thread(name="crawl",target=__execute_crawl,daemon=True,args=(config,logger,blacklist,batch_queue,token, float(seconds),only_once,diagnostics))
  thread.start()


