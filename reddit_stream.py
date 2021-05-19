from typing import Callable
from cancel_token import Cancel_Token
import praw
from praw.reddit import Reddit
import defines
from praw.models import SubredditHelper, Comment, Submission
from bot_blacklist import Threadsafe_Bot_Blacklist
from context import Thread_Safe_Context
from app_config import Config
from simple_logging import Logger
from diagnostics import Reddit_Crawl_Diagnostics
from subreddit import Subreddit_Batch_Queue, Subreddit_Batch
from time import sleep
import threading
import reddit_helper as rh

def handle_user(user_name: str, sub_name: str, context: Thread_Safe_Context):
  if context.blacklist.contains(user_name):
    context.crawl_diagnostics.increment_bots_detected()
    return
  new_user = False
  with context.current_data_lock:
    new_user = context.current_data.add_user(sub_name,user_name)
  if new_user:
    context.crawl_diagnostics.increment_usrers_extracted_total()

def handle_comment(comment: Comment, context: Thread_Safe_Context):
  if comment.author is None:
    context.crawl_diagnostics.increment_comments_no_author()
    return
  rh.scan_if_new_bot(comment,context)
  handle_user(comment.author.name,comment.subreddit.display_name, context)

def handle_post(post: Submission, context: Thread_Safe_Context):
  context.logger.log("Crawling submission: {mis}".format(mis=post.title))
  context.crawl_diagnostics.increment_submission_total()
  handle_user(post.author.name, post.subreddit.display_name, context)

  all_comments = rh.get_all_comments(post.comments)
  for comment in all_comments:
    context.crawl_diagnostics.increment_comments_total()
    handle_comment(comment, context)


def submit_batch_loop(monitor_type: str, context: Thread_Safe_Context, queue: Subreddit_Batch_Queue):
  #start of with some sleep as to not immediately try to submit an empty batch
  context.logger.log("Started batch save loop for {mt} stream".format(mt = monitor_type))
  sleep(context.config.stream_save_interval_seconds)
  while True:
    submit_batch_to_queue(context,queue)
    sleep(context.config.stream_save_interval_seconds)


def submit_batch_to_queue(context: Thread_Safe_Context, queue: Subreddit_Batch_Queue):
  old_batch = None
  new_batch = Subreddit_Batch()
  with context.current_data_lock:
    old_batch = context.current_data
    context.current_data = new_batch()
  queue.enqueue(old_batch)


def stream_monitor(monitor_type: str, stream_gen, data_handler, subs: SubredditHelper, reddit: Reddit, context: Thread_Safe_Context, queue: Subreddit_Batch_Queue, token: Cancel_Token):
  token.take_ownership(threading.get_ident())
  thread = threading.Thread(name="submit_thread_{monitor_type}",daemon=True, target=submit_batch_loop,args=(monitor_type,context,queue))
  thread.start()
  #pause after one repsone with nothing new to check if canceled, set to 0 for no delay
  context.logger.log("Start monitioring {mt} for subreddits {subs}".format(mt = monitor_type, subs = context.config.subreddits_to_crawl))
  for data in stream_gen(pause_after=1):
    if token.is_cancel_requested():
      context.logger.log("Terminating due to cancel request")
      break
    if data is None: 
      continue
    data_handler(data,context)
  queue.enqueue(context.current_data)
  context.logger.log("Stop monitoring of comments stream")
  token.inform_finsihed_cancel()

def comments_stream(subs: SubredditHelper, reddit: Reddit, context: Thread_Safe_Context, queue: Subreddit_Batch_Queue, token: Cancel_Token):
  stream_monitor("comments",subs.stream.comments,handle_comment,subs,reddit,context,queue,token)
  
def submission_stream(subs: SubredditHelper,reddit: Reddit, context: Thread_Safe_Context, queue: Subreddit_Batch_Queue, token: Cancel_Token):
  stream_monitor("submissions",subs.stream.submissions,handle_post,subs,reddit,context,queue,token)
  

def create_stream_monitor_thread(thread_name: str, target: Callable[[SubredditHelper,Reddit,Thread_Safe_Context,Subreddit_Batch_Queue,Cancel_Token],None],config: Config, logger:Logger, blacklist: Threadsafe_Bot_Blacklist, queue: Subreddit_Batch_Queue)-> Cancel_Token:
  reddit = praw.Reddit(
    client_id=defines.CLIENT_ID,
    client_secret=defines.CLIENT_SECRET,
    user_agent=defines.USER_AGENT)
  context = Thread_Safe_Context(reddit,config, Subreddit_Batch(),logger,blacklist, Reddit_Crawl_Diagnostics())

  subs_to_observe = rh.join_subreddits(config.subreddits_to_crawl)
  subs: SubredditHelper = reddit.subreddit(subs_to_observe)
  token: Cancel_Token = Cancel_Token()
  thread = threading.Thread(name=thread_name,target=target,args=(subs, reddit,context, queue, token))
  thread.start()
  return token

def create_comments_monitor_thread(config: Config, logger:Logger, blacklist: Threadsafe_Bot_Blacklist, queue: Subreddit_Batch_Queue)-> Cancel_Token:
  return create_stream_monitor_thread("comments_stream",comments_stream, config, logger, blacklist, queue)
  
def create_submission_monitor_thread(config: Config, logger:Logger, blacklist: Threadsafe_Bot_Blacklist, queue: Subreddit_Batch_Queue)-> Cancel_Token:
  return create_stream_monitor_thread("submission_stream",submission_stream,config,logger,blacklist,queue)

def run(config: Config, logger:Logger, blacklist: Threadsafe_Bot_Blacklist, queue: Subreddit_Batch_Queue)-> tuple[Cancel_Token,Cancel_Token]:
  comments_token = create_comments_monitor_thread(config,logger,blacklist,queue)
  submission_token = create_submission_monitor_thread(config,logger,blacklist,queue)
  return (comments_token,submission_token)
    
