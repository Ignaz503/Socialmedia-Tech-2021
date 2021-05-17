import subreddit
import bot_blacklist
from bot_blacklist import Bot_Blacklist
from simple_logging import Logger
import praw.models
from praw.models.comment_forest import CommentForest
from praw.models import Comment, Submission, Subreddit
from app_config import Config
from context import Context
from main import DATA_BASE_PATH

SOME_URL = "https://www.reddit.com/r/Veloren/comments/n4wwx7/server_issue/"
CLIENT_ID="oLm5KqTNCR5qrw"
CLIENT_SECRET="E-uXbSsa6JTNph_zp49vnbSLZpO0tg"
USER_AGENT="python:TUG-CommentCrawler:v1.0.0 (by u/Ignaz503)"

def handle_user(user_name: str, subreddit: Subreddit, submission: Submission, context: Context):
  if context.blacklist.contains(user_name):
    context.logger.log("Detected Bot {name}".format(name= user_name))
    return

  context.current_data.add_user(user_name)
  pass

def get_all_comments(forest: CommentForest):
  forest.replace_more(limit=None)
  return forest.list()

def scan_if_bot(comment: Comment, context: Context):  
  #todo maybe better check if user is bot
  if "I am a bot" in comment.body:
    context.logger.log("Detected New Bot: {name}".format(comment.auhtor.name))
    context.blacklist.add(comment.author.name)


def handle_comment(comment: Comment, subreddit: Subreddit, submission: Submission, context: Context):
  scan_if_bot(comment,context)
  handle_user(comment.author.name,subreddit, submission, context)

def handle_post(post: Submission, subreddit: Subreddit, context: Context):
  
  context.logger.log("Crawling submission: {mis}".format(mis=post.title))
  handle_user(post.author.name,subreddit,post, context)

  all_comments = get_all_comments(post.comments)
  for comment in all_comments:
    handle_comment(comment,subreddit, post, context)

def handle_subreddit(subreddit_name: str, context: Context):
  
  sub = context.reddit.subreddit(subreddit_name)

  context.logger.log("Crawling subreddit: {subreddit}".format(subreddit = sub.display_name))

  context.current_data = subreddit.load(DATA_BASE_PATH,sub.display_name)

  try:
    for submission in context.config.submission_getter.get(sub,context.config.number_of_posts, context.logger):
      handle_post(submission,sub,context)
  except Exception as err:
    print(err)
  finally:
    context.logger.log("Finished Crawling subreddit: {subreddit}. Saving data.".format(subreddit = sub.display_name))
    context.current_data.save_to_file(DATA_BASE_PATH)
    print("Saved {subreddit} data to disk".format(subreddit = sub.display_name))

def save(context: Context):
  context.blacklist.save_to_file(bot_blacklist.FILE)

def run(config: Config, logger: Logger):
  reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT)

  blacklist: Bot_Blacklist = bot_blacklist.load(bot_blacklist.FILE)
  context = Context(reddit,config, None,logger,blacklist)

  for subreddit in config.subreddits_to_crawl:
    handle_subreddit(subreddit,context)
  
  save(context)


