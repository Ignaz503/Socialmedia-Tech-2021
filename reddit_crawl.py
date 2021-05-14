import praw
import praw.models
from praw.reddit import Comment, Submission

SOME_URL = "https://www.reddit.com/r/hmmm/comments/nc3d8c/hmmm/"
CLIENT_ID="oLm5KqTNCR5qrw"
CLIENT_SECRET="E-uXbSsa6JTNph_zp49vnbSLZpO0tg"
USER_AGENT="Comment Extraction (by u/Ignaz503)"

def print_comment(the_comment: Comment):
  print(the_comment.author.name +" says: '" + the_comment.body+"'")

def main():
  reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT)

  submission: Submission = reddit.submission(url=SOME_URL)
  submission.comments.replace_more(limit=0)
  for top_level_comment in submission.comments:
    print_comment(top_level_comment)

if __name__ == "__main__":
  main()