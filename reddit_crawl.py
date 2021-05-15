import praw
import praw.models
from praw.models.comment_forest import CommentForest
from praw.reddit import Comment, Submission
import json

import user_tests

SOME_URL = "https://www.reddit.com/r/Veloren/comments/n4wwx7/server_issue/"
CLIENT_ID="oLm5KqTNCR5qrw"
CLIENT_SECRET="E-uXbSsa6JTNph_zp49vnbSLZpO0tg"
USER_AGENT="Comment Extraction (by u/Ignaz503)"

def print_comment(the_comment: Comment):
  comment_dict={
    "redditor": the_comment.author.name,
    "body": the_comment.body,
    "score": the_comment.score
  }
  print(json.dumps(comment_dict))

def get_all_comments(forest: CommentForest):
  forest.replace_more(limit=None)
  return forest.list()

def handle_post(post: Submission):
  all_comments = get_all_comments(post.comments)
  for comment in all_comments:
    print_comment(comment)

def run_tests():
  user_tests.load_test()

def main():
  reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT)
  re: praw.models.Subreddit = reddit.subreddit("redditdev")
  print(type(re.subscribers))
  #submission: Submission = reddit.submission(url=SOME_URL)
  #handle_post(submission)

if __name__ == "__main__":
  main()