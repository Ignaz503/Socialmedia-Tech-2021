import string
import random
import jsonpickle
import users
from users import Users

def random_string(length: int = 10)-> str:
  return ''.join(random.choice(string.ascii_letters) for i in range(0,length))

class User_Tests:
  def __init__(self) -> None:
      pass

  def run_all(self):
    self.random_user_serialize_test()
    self.load_test()
    self.all_pair_test()

  def random_users(self, num: int = 10):
    users = Users()
    for i in range(0,num):
      users.add_user_init(random_string(),random_string())
    return users

  def random_user_serialize_test(self):
    rando = self.random_users()
    js = rando.to_json()
    print(js)
    deser: Users = jsonpickle.decode(js)
    deser.print_user_names()

  def load_test(self):
    my_users = users.load(users.USER_FILE)
    my_users.print_user_names()

  def all_pair_test(self):
    users = self.random_users()
    for user in users.data:
      for i in range(0,7):
        users.add_subreddit_for_user(user,random_string())
    #print all pairs
    for my_user in users.generate_subreddit_pairs_for_all_users():
      print(users.data[my_user[0]])
      print(my_user[1])
      input("next user?")

def run_all():
  User_Tests().run_all()