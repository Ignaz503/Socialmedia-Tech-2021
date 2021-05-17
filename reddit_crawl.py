import bot_blacklist
from bot_blacklist import Bot_Blacklist
from simple_logging import Logger
import praw
import praw.models
from praw.models.comment_forest import CommentForest
from praw.models import Comment, Submission, Subreddit
from praw.reddit import Reddit
import users
from users import Users
import sys
import tests
import crawl_config
from crawl_config import Config

class Context:
  reddit: Reddit
  config: Config
  userDB: Users
  logger: Logger
  blacklist: Bot_Blacklist

  def __init__(self, reddit: Reddit,config: Config, userDB: Users, logger: Logger, blacklist: Bot_Blacklist) -> None:
      self.reddit = reddit
      self.config = config 
      self.userDB = userDB
      self.logger = logger
      self.blacklist = blacklist


SOME_URL = "https://www.reddit.com/r/Veloren/comments/n4wwx7/server_issue/"
CLIENT_ID="oLm5KqTNCR5qrw"
CLIENT_SECRET="E-uXbSsa6JTNph_zp49vnbSLZpO0tg"
USER_AGENT="python:TUG-CommentCrawler:v1.0.0 (by u/Ignaz503)"

def handle_user(user_name: str, subreddit: Subreddit, submission: Submission, context: Context):
  #todo check if user is bot

  if context.blacklist.contains(user_name):
    context.logger.log("Detected Bot {name}".format(name= user_name))
    return

  context.userDB.add_subreddit_for_user(user_name,subreddit.display_name)
  pass

def get_all_comments(forest: CommentForest):
  forest.replace_more(limit=None)
  return forest.list()

def scan_if_bot(comment: Comment, context: Context):  
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

  try:
    for submission in context.config.submission_getter.get(sub,context.config.number_of_posts, context.logger):
      handle_post(submission,sub,context)
  except:
    context.logger.log("something went wrong whilst crawling. saving what's crawled so far")

def save(context: Context):
  context.userDB.save_to_file(users.FILE)
  context.blacklist.save_to_file(bot_blacklist.FILE)

def main(args: list[str]):

  if "-test" in args:
    tests.run()
    return

  reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT)

  userDB = users.load(users.FILE)
  config = crawl_config.load(crawl_config.FILE)
  logger: Logger = Logger(config.verbose)
  blacklist: Bot_Blacklist = bot_blacklist.load(bot_blacklist.FILE)
  context = Context(reddit,config, userDB,logger,blacklist)

  #todo read config
  for subreddit in config.subreddits_to_crawl:
    handle_subreddit(subreddit,context)
  
  save(context)


if __name__ == "__main__":
  main(sys.argv)