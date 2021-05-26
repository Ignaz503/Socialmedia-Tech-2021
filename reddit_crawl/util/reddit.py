from praw import Reddit
from prawcore.exceptions import OAuthException

def authenticate(reddit: Reddit)->bool:
  """
    returns true if reddit instance is authenticated
    returns false if not
  """
  try:
      reddit.user.me()
  except OAuthException:
      return False
  else:
      return True