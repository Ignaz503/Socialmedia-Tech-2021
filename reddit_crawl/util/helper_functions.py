from utility.simple_logging import Level
from utility.cancel_token import Cancel_Token
import threading
from time import sleep
from praw.models import Comment
from praw.models import Submission
from reddit_crawl.util.context import Context, Thread_Safe_Context
from praw.models.comment_forest import CommentForest
from reddit_crawl.data.subreddit import Subreddit_Batch_Queue, Subreddit_Batch

def get_all_comments(forest: CommentForest):
  forest.replace_more(limit=None)
  return forest.list()

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
  if comment.author is None:
    context.crawl_diagnostics.increment_comments_no_author()
    return
  scan_if_new_bot(comment,context)
  handle_user_thread_safe(comment.author.name,comment.subreddit.display_name, context)

def handle_post_thread_safe(post: Submission, context: Thread_Safe_Context, token: Cancel_Token):
  context.logger.log("Crawling submission: {mis}".format(mis=post.title),Level.INFO)
  context.crawl_diagnostics.increment_submission_total()
  if post.author is not None:
    handle_user_thread_safe(post.author.name, post.subreddit.display_name, context)

  all_comments = get_all_comments(post.comments)
  for comment in all_comments:
    if token.is_cancel_requested():
      break
    context.crawl_diagnostics.increment_comments_total()
    handle_comment_thread_safe(comment, context,token)


def __submit_batch_loop(monitor_type: str, context: Thread_Safe_Context, queue: Subreddit_Batch_Queue):
  #start of with some sleep as to not immediately try to submit an empty batch
  context.logger.log("Started batch save loop for {mt}".format(mt = monitor_type),Level.INFO)
  sleep(context.config.stream_save_interval_seconds)
  while True:
    __submit_batch_to_queue(context,queue)
    sleep(context.config.stream_save_interval_seconds)


def __submit_batch_to_queue(context: Thread_Safe_Context, queue: Subreddit_Batch_Queue):
  old_batch = None
  new_batch = Subreddit_Batch()
  with context.current_data_lock:
    old_batch = context.current_data
    context.current_data = new_batch()
  queue.enqueue(old_batch)

def start_batch_submit_thread(name_specifier:str, context: Thread_Safe_Context, queue: Subreddit_Batch_Queue):
  thread = threading.Thread(name="submit_thread {monitor_type}",daemon=True, target=__submit_batch_loop,args=(name_specifier,context,queue))
  thread.start()