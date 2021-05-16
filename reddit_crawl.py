from warnings import catch_warnings
import praw
import praw.models
from praw.models.comment_forest import CommentForest
from praw.models import Comment, Submission, Subreddit
from praw.reddit import Reddit
import users
from users import Users
import sys

SOME_URL = "https://www.reddit.com/r/Veloren/comments/n4wwx7/server_issue/"
CLIENT_ID="oLm5KqTNCR5qrw"
CLIENT_SECRET="E-uXbSsa6JTNph_zp49vnbSLZpO0tg"
USER_AGENT="python:TUG-CommentCrawler:v1.0.0 (by u/Ignaz503)"

def print_comment(the_comment: Comment):
  comment_dict={
    "redditor": the_comment.author.name,
    "body": the_comment.body,
    "score": the_comment.score
  }
  print(comment_dict)

def get_all_comments(forest: CommentForest):
  forest.replace_more(limit=None)
  return forest.list()

def handle_comment(comment: Comment, reddit: Reddit, subreddit: Subreddit, userDB: Users):
  userDB.add_subreddit_for_user(comment.author.name,subreddit.display_name)

def handle_post(post: Submission, reddit: Reddit, subreddit: Subreddit, userDB: Users):
  
  userDB.add_subreddit_for_user(post.author.name, subreddit.display_name)

  all_comments = get_all_comments(post.comments)
  for comment in all_comments:
    print_comment(comment)

def handle_subreddit(reddit: praw.Reddit, subreddit_name: str):
  userDB = users.load(users.FILE)
  sub = reddit.subreddit(subreddit_name)
  
  try:
    #todo figure out from where and how many post
    posts = [] 
    for submission in posts:
      handle_post(submission,reddit,sub,userDB)
  except:
    print("something went wrong whilst crawling. saving what's crawled so far")
  userDB.save_to_file(users.FILE)

def dummy(reddit: praw.Reddit, subreddit_name: str):
  sub: Subreddit = reddit.subreddit(subreddit_name)
  for post in sub.hot(limit= 10):
    print(post.title)

def main(args: list[str]):
  reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT)
  
  if len(args) < 2:
    return

  args.pop(0)
  for sub in args:
    handle_subreddit(reddit, sub)


if __name__ == "__main__":
  main(sys.argv)