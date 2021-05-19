from diagnostics import  Reddit_Crawl_Diagnostics
from subreddit import Subreddit_Batch_Queue, Subreddit_Batch
from bot_blacklist import Threadsafe_Bot_Blacklist
from simple_logging import Logger
import praw.models
from praw.models import Comment, Submission
from app_config import Config
from context import Context
import defines
import traceback
import reddit_helper as rh

def handle_user(user_name: str, sub_name: str, context: Context):
  if context.blacklist.contains(user_name):
    context.crawl_diagnostics.increment_bots_detected()
    return

  new_user = context.current_data.add_user(sub_name,user_name)
  if new_user:
    context.crawl_diagnostics.increment_usrers_extracted_total()
  pass

def handle_comment(comment: Comment, submission: Submission, context: Context):
  if comment.author is None:
    context.crawl_diagnostics.increment_comments_no_author()
    return
  rh.scan_if_new_bot(comment,context)
  handle_user(comment.author.name,submission.subreddit.display_name, context)

def handle_post(post: Submission, context: Context):
  
  context.logger.log("Crawling submission: {mis}".format(mis=post.title))
  context.crawl_diagnostics.increment_submission_total()
  handle_user(post.author.name, post.subreddit.display_name, context)

  all_comments = rh.get_all_comments(post.comments)
  for comment in all_comments:
    context.crawl_diagnostics.increment_comments_total()
    handle_comment(comment, post, context)


def handle_crawl(context: Context):
  
  for sub in context.config.subreddits_to_crawl:
    subreddit = context.reddit.subreddit(sub)
    context.logger.log("Crawling subreddits: {subreddit}".format(subreddit = sub))
    try:
      for submission in context.config.submission_getter.get(subreddit,context.config.number_of_posts, context.logger):
        handle_post(submission, context)
    except Exception as err:
      print(err)
      traceback.print_tb(err.__traceback__)


def run(config: Config, logger: Logger, blacklist: Threadsafe_Bot_Blacklist, batch_queue: Subreddit_Batch_Queue):
  reddit = praw.Reddit(
    client_id=defines.CLIENT_ID,
    client_secret=defines.CLIENT_SECRET,
    user_agent=defines.USER_AGENT)

  context = Context(reddit,config, Subreddit_Batch(),logger,blacklist, Reddit_Crawl_Diagnostics())

  handle_crawl(context)

  batch_queue.enqueue(context.current_data)
  context.crawl_diagnostics.end_timing()
  context.crawl_diagnostics.log(context.logger)


