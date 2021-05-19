from context import Context
from praw.models.comment_forest import CommentForest
from praw.models import Comment
from typing import Callable

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
