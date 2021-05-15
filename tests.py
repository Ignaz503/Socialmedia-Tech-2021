import string
import random
import json
import users
from users import Users
import subreddit
from subreddit import Subreddits

def random_string(length: int = 10)-> str:
  return ''.join(random.choice(string.ascii_letters) for i in range(0,length))

class User_Tests:
  def __init__(self) -> None:
      pass

  def run_all(self):
    self.random_user_serialize_test()
    self.load_test()

  def random_users(self, num: int = 10):
    users = Users()
    for i in range(0,num):
      users.get_or_add_user(random_string(),random_string())
    return users

  def random_user_serialize_test(self):
    rando = self.random_users()
    js = rando.to_json()
    print(js)
    deser = json.loads(js)
    new = Users(deser)
    new.print_user_names()

  def load_test(self):
    my_users = users.load(users.USER_FILE)
    my_users.print_user_names()

class Subreddit_Test:
  def __init__(self) -> None:
      pass

  def run_all(self):
    self.random_subreddit_serialize_test()
    self.load_test()

  def random_subreddits(self, num: int = 10) -> Subreddits:
    subreddits = Subreddits()
    for i in range(0,num):
      name = random_string()
      id = random_string(5)
      count = random.randint(0,1000000)
      subreddits.get_or_add_subreddit(name,id,count)
    return subreddits

  def random_subreddit_serialize_test(self):
    rando = self.random_subreddits()
    js = rando.to_json()
    print(js)
    deser = json.loads(js)
    new = Subreddits(deser)
    new.print_subreddit_names()

  def load_test(self):
    my_subs = subreddit.load(subreddit.SUBREDDIT_FILE)
    my_subs.print_subreddit_names()

def run_all():
  User_Tests().run_all()
  Subreddit_Test().run_all()