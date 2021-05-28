from utility.simple_logging import Level
from utility.cancel_token import Cancel_Token
import threading
import time
from praw.models import Comment
from praw.models import Submission, MoreComments
from reddit_crawl.util.context import Context, Thread_Safe_Context
from praw.models.comment_forest import CommentForest
from reddit_crawl.data.subreddit import Subreddit_Batch_Queue, Subreddit_Batch
from defines import MAX_COMMENT_NUM
from utility.simple_logging import Logger, Level
from typing import Callable


def handle_all_comments(comment_handler: Callable[[Comment,Thread_Safe_Context,Cancel_Token],None],submission: Submission, context: Thread_Safe_Context, token: Cancel_Token):
  more_comments: list[MoreComments] = []
  more_comments.extend(submission.comments.replace_more())
  context.logger.log("Handling initial comment forest")
  #handle initial forest
  for comment in submission.comments.list():
    if token.is_cancel_requested():
      break
    if isinstance(comment, MoreComments):
      #maybe not needed
      more_comments.append(comment)
      continue
    comment_handler(comment,context,token)

  if token.is_cancel_requested():
    return
  context.logger.log("Handling more comments")
  while len(more_comments) > 0:
    if token.is_cancel_requested():
      return
    more_comment = more_comments.pop(0)
    for comment in more_comment.comments():
      if token.is_cancel_requested():
        break
      if isinstance(comment, MoreComments):
        context.logger.log("found even more comments to handle, whilst handling more comments")
        more_comments.append(comment)
        continue
      context.crawl_diagnostics.increment_comments_total()
      comment_handler(comment,context,token) 

def join_subreddits(subs: list[str]):
  return "+".join(subs)

def scan_if_new_bot(comment: Comment, context: Context):  
  #todo maybe better check if user is bot
  if "I am a bot" in comment.body and not context.blacklist.contains(comment.author.name):
    context.crawl_diagnostics.increment_new_bots_total()
    context.blacklist.add(comment.author.name)

def handle_user_thread_safe(user_name: str, sub_name: str, context: Thread_Safe_Context):
  if context.blacklist.contains(user_name):
    context.crawl_diagnostics.increment_bots_detected()
    return
  new_user = False
  with context.current_data_lock:
    new_user = context.current_data.add_user(sub_name,user_name)
  if new_user:
    context.crawl_diagnostics.increment_usrers_extracted_total()

def handle_comment_thread_safe(comment: Comment, context: Thread_Safe_Context, token: Cancel_Token):
  if token.is_cancel_requested():
    return
  context.crawl_diagnostics.increment_comments_total()
  if comment.author is None:
    context.crawl_diagnostics.increment_comments_no_author()
    return

  if context.current_data.conatins_user(comment.author.name,comment.subreddit.display_name):
    #we already found this user once for this subreddit
    return

  scan_if_new_bot(comment,context)
  handle_user_thread_safe(comment.author.name,comment.subreddit.display_name, context)

def handle_post_thread_safe(post: Submission, context: Thread_Safe_Context, token: Cancel_Token):
  context.logger.log("Crawling submission: {mis}".format(mis=post.title),Level.INFO)
  context.crawl_diagnostics.increment_submission_total()
  if post.author is not None:
    handle_user_thread_safe(post.author.name, post.subreddit.display_name, context)

  handle_all_comments(handle_comment_thread_safe,post,context,token)


def __submit_batch_loop(monitor_type: str, context: Thread_Safe_Context, queue: Subreddit_Batch_Queue, token: Cancel_Token):
  #start of with some sleep as to not immediately try to submit an empty batch
  with token:
    context.logger.log("Started batch save loop for {mt}".format(mt = monitor_type),Level.INFO)
    current_time = time.perf_counter()
    last_execution =  current_time # start sleeping
    while not token.is_cancel_requested():
      if current_time - last_execution >= context.config.stream_save_interval_seconds:
        last_execution = current_time
        __submit_batch_to_queue(context,queue)
      current_time = time.perf_counter()

def __submit_batch_to_queue(context: Thread_Safe_Context, queue: Subreddit_Batch_Queue):
  old_batch = None
  new_batch = Subreddit_Batch()
  with context.current_data_lock:
    old_batch = context.current_data
    context.current_data = new_batch
  queue.enqueue(old_batch)

def start_batch_submit_thread(name_specifier:str, context: Thread_Safe_Context, queue: Subreddit_Batch_Queue, token: Cancel_Token):
  thread = threading.Thread(name="submit_thread {monitor_type}",daemon=True, target=__submit_batch_loop,args=(name_specifier,context,queue,token))
  thread.start()