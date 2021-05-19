from threading import Thread
from types import new_class
from typing import ChainMap
from cancel_token import Cancel_Token
import praw
from praw.reddit import Reddit
import defines
from praw.models import SubredditHelper, Comment, Submission
from praw.models.comment_forest import CommentForest
from bot_blacklist import Threadsafe_Bot_Blacklist
from context import Thread_Safe_Context
from app_config import Config
from simple_logging import Logger
from diagnostics import Reddit_Crawl_Diagnostics
from subreddit import Subreddit_Batch_Queue, Subreddit_Batch
from enum import Enum
from time import sleep
import threading
import reddit_helper as rh

def handle_user(user_name: str, sub_name: str, context: Thread_Safe_Context):
  if context.blacklist.contains(user_name):
    context.subreddit_diagnostics.increment_bots_detected()
    return
  new_user = False
  with context.current_data_lock:
    new_user = context.current_data.add_user(sub_name,user_name)
  if new_user:
    context.subreddit_diagnostics.increment_usrers_extracted_total()
  pass


def handle_comment(comment: Comment, context: Thread_Safe_Context):
  if comment.author is None:
    context.subreddit_diagnostics.increment_comments_no_author()
    return
  rh.scan_if_new_bot(comment,context)
  handle_user(comment.author.name,comment.subreddit.display_name, context)

def handle_post(post: Submission, context: Thread_Safe_Context):
  
  context.logger.log("Crawling submission: {mis}".format(mis=post.title))
  context.subreddit_diagnostics.increment_submission_total()
  handle_user(post.author.name, post.subreddit.display_name, context)

  all_comments = rh.get_all_comments(post.comments)
  for comment in all_comments:
    context.subreddit_diagnostics.increment_comments_total()
    handle_comment(comment, post, context)


def submit_batch_loop(context: Thread_Safe_Context, queue: Subreddit_Batch_Queue):
  #start of with some sleep as to not immediately try to submit an empty batch
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

def comments_stream(subs: SubredditHelper, reddit: Reddit, context: Thread_Safe_Context, queue: Subreddit_Batch_Queue, token: Cancel_Token):
  token.take_ownership(threading.get_ident())
  thread = threading.Thread(name="submit_thread_comments",daemon=True, target=submit_batch_loop,args=(context,queue))
  thread.start()
  for comment in subs.stream.comments():
    if(token.is_cancel_requested()):
      break
    handle_comment(comment,context)   
  queue.enqueue(context.current_data)
  token.inform_finsihed_cancel()

def submission_stream(subs: SubredditHelper,reddit: Reddit, context: Thread_Safe_Context, queue: Subreddit_Batch_Queue, token: Cancel_Token):
  token.take_ownership(threading.get_ident())
  thread = threading.Thread(name="submit_thread_comments",daemon=True, target=submit_batch_loop,args=(context,queue))
  thread.start()
  for submission in subs.stream.submissions():
    if(token.is_cancel_requested()):
      break
    handle_post(submission,context)
  queue.enqueue(context.current_data)
  token.inform_finsihed_cancel()


def create_comments_stream_tread(config: Config, logger:Logger, blacklist: Threadsafe_Bot_Blacklist, queue: Subreddit_Batch_Queue)-> Cancel_Token:
  reddit = praw.Reddit(
    client_id=defines.CLIENT_ID,
    client_secret=defines.CLIENT_SECRET,
    user_agent=defines.USER_AGENT)
  context = Thread_Safe_Context(reddit,config, Subreddit_Batch(),logger,blacklist, Reddit_Crawl_Diagnostics())

  subs_to_observe = rh.join_subreddits(config.subreddits_to_crawl)
  logger.log(subs_to_observe)
  subs: SubredditHelper = reddit.subreddit(subs_to_observe)
  token: Cancel_Token = Cancel_Token()
  thread = threading.Thread(name="comments_stream",target=comments_stream,args=(subs, reddit,context, queue, token))
  thread.start()
  return token

def create_submission_stream_thread(config: Config, logger:Logger, blacklist: Threadsafe_Bot_Blacklist, queue: Subreddit_Batch_Queue)-> Cancel_Token:
  reddit = praw.Reddit(
    client_id=defines.CLIENT_ID,
    client_secret=defines.CLIENT_SECRET,
    user_agent=defines.USER_AGENT)
  context = Thread_Safe_Context(reddit,config, Subreddit_Batch(),logger,blacklist, Reddit_Crawl_Diagnostics())

  subs_to_observe = rh.join_subreddits(config.subreddits_to_crawl)
  logger.log(subs_to_observe)
  subs: SubredditHelper = reddit.subreddit(subs_to_observe)
  token: Cancel_Token = Cancel_Token()
  thread = threading.Thread(name="submission_stream",target=submission_stream,args=(subs, reddit,context, queue, token))
  thread.start()

  return token


def run(config: Config, logger:Logger, blacklist: Threadsafe_Bot_Blacklist, queue: Subreddit_Batch_Queue)-> tuple[Cancel_Token,Cancel_Token]:
  comments_token = create_comments_stream_tread(config,logger,blacklist,queue)
  submission_token = create_submission_stream_thread(config,logger,blacklist,queue)
  return (comments_token,submission_token)
    
