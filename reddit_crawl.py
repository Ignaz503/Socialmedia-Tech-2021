from cancel_token import Cancel_Token
import threading
import traceback
import praw.models
import reddit_helper as rh
import time
from context import Context
from app_config import Config
from simple_logging import Logger
from cancel_token import Cancel_Token
from praw.models import Comment, Submission
from diagnostics import  Reddit_Crawl_Diagnostics
from bot_blacklist import Threadsafe_Bot_Blacklist
from subreddit import Subreddit_Batch_Queue, Subreddit_Batch
from defines import CLIENT_ID, CLIENT_SECRET, USER_AGENT, MIN_REPEAT_TIME

def __handle_user(user_name: str, sub_name: str, context: Context):
  if context.blacklist.contains(user_name):
    context.crawl_diagnostics.increment_bots_detected()
    return
  new_user = context.current_data.add_user(sub_name,user_name)
  if new_user:
    context.crawl_diagnostics.increment_usrers_extracted_total()


def __handle_comment(comment: Comment, submission: Submission, context: Context):
  if comment.author is None:
    context.crawl_diagnostics.increment_comments_no_author()
    return
  rh.scan_if_new_bot(comment,context)
  __handle_user(comment.author.name,submission.subreddit.display_name, context)

def __handle_post(post: Submission, context: Context):
  
  context.logger.log("Crawling submission: {mis}".format(mis=post.title))
  context.crawl_diagnostics.increment_submission_total()
  __handle_user(post.author.name, post.subreddit.display_name, context)

  all_comments = rh.get_all_comments(post.comments)
  for comment in all_comments:
    context.crawl_diagnostics.increment_comments_total()
    __handle_comment(comment, post, context)


def __handle_crawl(context: Context):
  for sub in context.config.subreddits_to_crawl:
    subreddit = context.reddit.subreddit(sub)
    context.logger.log("Crawling subreddits: {subreddit}".format(subreddit = sub))
    try:
      for submission in context.config.submission_getter.get(subreddit,context.config.number_of_posts, context.logger):
        __handle_post(submission, context)
    except Exception as err:
      print(err)
      traceback.print_tb(err.__traceback__)

def __handle_repeat_execution(config: Config, logger: Logger, batch_queue: Subreddit_Batch_Queue, bot_list: Threadsafe_Bot_Blacklist) -> Cancel_Token:
  seconds = config.get_repeat_time_in_seconds()
  only_once = False
  if seconds == 0:
    only_once = True

  if seconds < MIN_REPEAT_TIME:
    seconds = MIN_REPEAT_TIME
  token = Cancel_Token()
  #run once not on main thread
  thread = threading.Thread(name="crawl",target=__execute_crawl,daemon=True,args=(config,logger,bot_list,batch_queue,token, float(seconds),only_once))
  thread.start()

  return token

def __execute_crawl(config: Config, logger: Logger, blacklist: Threadsafe_Bot_Blacklist, batch_queue: Subreddit_Batch_Queue,token: Cancel_Token, wait_period_seconds: float, only_once: bool):

  token.take_ownership(threading.get_ident())
  try:
    reddit = praw.Reddit(
      client_id=CLIENT_ID,
      client_secret=CLIENT_SECRET,
      user_agent=USER_AGENT)
    context = Context(reddit,config, Subreddit_Batch(),logger,blacklist, Reddit_Crawl_Diagnostics())
    logger.log("executing crawl every {s} seconds".format(s = wait_period_seconds))
    current_time = time.time()
    last_execution = float('-inf')
    while not token.is_cancel_requested():
      if current_time - last_execution >= wait_period_seconds:
        last_execution = current_time
        __handle_crawl(context)
        batch_queue.enqueue(context.current_data)
        context.crawl_diagnostics.end_timing()
        context.crawl_diagnostics.log(context.logger)
      if only_once:
        break
      current_time = time.time()

    batch_queue.enqueue(context.current_data)
    token.inform_finsihed_cancel()
  finally:
    token.inform_finsihed_cancel()


def run(config: Config, logger: Logger, blacklist: Threadsafe_Bot_Blacklist, batch_queue: Subreddit_Batch_Queue) -> Cancel_Token:
  return __handle_repeat_execution(config,logger,batch_queue,blacklist)


