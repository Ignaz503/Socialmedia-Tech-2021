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

def run_all():
  User_Tests().run_all()