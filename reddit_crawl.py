from diagnostics import Diagnostics, Reddit_Crawl_Diagnostics, Subreddit_Crawl_Diagnostic
import subreddit
import bot_blacklist
from bot_blacklist import Bot_Blacklist
from simple_logging import Logger
import praw.models
from praw.models.comment_forest import CommentForest
from praw.models import Comment, Submission, Subreddit
from app_config import Config
from context import Context
import defines
import traceback

def handle_user(user_name: str, subreddit: Subreddit, submission: Submission, context: Context):
  if context.blacklist.contains(user_name):
    context.subreddit_diagnostics.increment_bots_detected()
    return

  new_user = context.current_data.add_user(user_name)
  if new_user:
    context.subreddit_diagnostics.increment_new_usrers_total()
  pass

def get_all_comments(forest: CommentForest):
  forest.replace_more(limit=None)
  return forest.list()

def scan_if_bot(comment: Comment, context: Context):  
  #todo maybe better check if user is bot
  if "I am a bot" in comment.body and not context.blacklist.contains(comment.author.name):
    context.subreddit_diagnostics.increment_new_bots_total()
    context.blacklist.add(comment.author.name)


def handle_comment(comment: Comment, subreddit: Subreddit, submission: Submission, context: Context):
  if comment.author is None:
    context.subreddit_diagnostics.increment_comments_no_author()
    return
  
  scan_if_bot(comment,context)
  handle_user(comment.author.name,subreddit, submission, context)

def handle_post(post: Submission, subreddit: Subreddit, context: Context):
  
  context.logger.log("Crawling submission: {mis}".format(mis=post.title))
  context.subreddit_diagnostics.increment_submission_total()
  handle_user(post.author.name,subreddit,post, context)

  all_comments = get_all_comments(post.comments)
  for comment in all_comments:
    context.subreddit_diagnostics.increment_comments_total()
    handle_comment(comment,subreddit, post, context)

def handle_subreddit_diagnostics(context: Context):
    context.subreddit_diagnostics.log(context.logger)
    context.crawl_diagnostics.accumulate_subreddit_data(context.subreddit_diagnostics)
    context.subreddit_diagnostics.reset()

def handle_subreddit(subreddit_name: str, context: Context):
  
  sub = context.reddit.subreddit(subreddit_name)

  context.logger.log("Crawling subreddit: {subreddit}".format(subreddit = sub.display_name))
  context.subreddit_diagnostics.name = sub.display_name

  context.current_data = subreddit.load(defines.DATA_BASE_PATH,sub.display_name)
  context.crawl_diagnostics.increment_subreddits_total()
  try:
    for submission in context.config.submission_getter.get(sub,context.config.number_of_posts, context.logger):
      handle_post(submission,sub,context)
  except Exception as err:
    print(err)
    traceback.print_tb(err.__traceback__)
  finally:
    context.subreddit_diagnostics.end_timing()
    context.logger.log("Finished Crawling subreddit: {subreddit}.".format(subreddit = sub.display_name))
    handle_subreddit_diagnostics(context)
    context.logger.log("Saving data.")
    context.current_data.save_to_file(defines.DATA_BASE_PATH)
    print("Saved {subreddit} data to disk".format(subreddit = sub.display_name))

def save(context: Context):
  context.blacklist.save_to_file(bot_blacklist.FILE)

def run(config: Config, logger: Logger):
  reddit = praw.Reddit(
    client_id=defines.CLIENT_ID,
    client_secret=defines.CLIENT_SECRET,
    user_agent=defines.USER_AGENT)

  blacklist: Bot_Blacklist = bot_blacklist.load(bot_blacklist.FILE)
  context = Context(reddit,config, None,logger,blacklist, Subreddit_Crawl_Diagnostic(), Reddit_Crawl_Diagnostics())

  for subreddit in config.subreddits_to_crawl:
    handle_subreddit(subreddit,context)
  
  context.crawl_diagnostics.end_timing()
  context.crawl_diagnostics.log(context.logger)
  save(context)


