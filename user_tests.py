import string
import random

import users
from users import Users

def run_all():
  random_user_test()

def random_string(length: int = 10)-> str:
  return ''.join(random.choice(string.ascii_letters) for i in range(0,length))

def random_users(num: int = 10):
  users = Users()
  for i in range(0,num):
    users.try_add_new_user(random_string(),random_string())
  return users

def random_user_test():
  rando = random_users()
  print(rando.to_json())

def load_test():
  my_users = users.load(users.USER_FILE)
  print(my_users.to_json())