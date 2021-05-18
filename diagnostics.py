from typing import Any
from simple_logging import Logger

class Data_Handler:
  def __init__(self) -> None:
    pass
  def update(self, current_value, new_value):
    return None
  def log(self, value, logger: Logger):
    pass
  def init_value(self):
    return None


class Diagnostics:
  data: dict[str, Any]
  data_handler: dict[str,Data_Handler]

  def __init__(self) -> None:
      self.data = {}
      self.data_handler = {}
  
  def create_category(self, name: str, handler: Data_Handler):
    self.data[name] = handler.init_value()
    self.data_handler[name] = handler

  def update_value(self, category: str, data):
    if category in self.data:
      old_val = self.data[category]
      self.data[category] = self.data_handler[category].update(old_val,data)
  
  def display_category(self, category: str, logger: Logger):
    if category in self.data:
      self.data_handler[category].log(self.data[category],logger)

  def get(self, category: str):
    if category in self.data:
      return self.data[category]
    return None

  def log(self, logger: Logger):
    for key in self.data:
      self.display_category(key,logger)

  def reset(self):
    for key in self.data:
      self.data[key] = self.data_handler[key].init_value()

class Increment_Data_Handler(Data_Handler):
    start_value: int
    def __init__(self, start_value) -> None:
      self.start_value = start_value
    
    def update(self, current_value, new_value):
      return current_value + new_value
      
    def log(self, value, logger: Logger):
      logger.log(self.build_message(value))
    
    def build_message(self, value):
      return value

    def init_value(self):
      return self.start_value

class Total_Of_Incremnt_Data_Handler(Increment_Data_Handler):
  message_end: str
  def __init__(self, start_value = 0, message_end: str = "") -> None:
      super().__init__(start_value)
      self.message_end = message_end
  def build_message(self, value):
    return "A total of {val} ".format(val = value) + self.message_end

class Subreddit_Crawl_Diagnostic(Diagnostics):
  comments_total ="comments_total"
  comments_no_auhtor = "comments_no_auhtor"
  bots_detected = "bots_detected"  
  new_bots_detected = "new_bots_detected"
  submissions_total = "submissions_total" 
  new_users = "new_users"
  name: str
  def __init__(self) -> None:
      super().__init__()
      self.name = ""
      self.create_category(self.comments_total,Total_Of_Incremnt_Data_Handler(message_end="comments have been crawled"))
      self.create_category(self.comments_no_auhtor, Total_Of_Incremnt_Data_Handler(message_end="comments have had no author"))
      self.create_category(self.bots_detected, Total_Of_Incremnt_Data_Handler(message_end="bots have been detected (not unique)"))
      self.create_category(self.new_bots_detected, Total_Of_Incremnt_Data_Handler(message_end="new bots have been detected"))
      self.create_category(self.submissions_total,Total_Of_Incremnt_Data_Handler(message_end="submissions have been crawled"))     
      self.create_category(self.new_users, Total_Of_Incremnt_Data_Handler(message_end="new users have been detected"))
  
  def increment_comments_total(self):
    self.update_value(self.comments_total,1) 
  
  def increment_new_usrers_total(self):
    self.update_value(self.new_users,1) 

  def increment_comments_no_author(self):
    self.update_value(self.comments_no_auhtor,1)
  
  def increment_bots_detected(self):
    self.update_value(self.bots_detected,1)
  
  def increment_submission_total(self):
    self.update_value(self.submissions_total,1)
  
  def increment_new_bots_total(self):
    self.update_value(self.new_bots_detected,1)

  def log(self, logger: Logger):
    logger.log("-"*15 + self.name + "-"*15)
    super().log(logger)
    logger.log("-"*30)


class Reddit_Crawl_Diagnostics(Diagnostics):
  submissions_total = "submissions_total"
  subreddits_total ="subreddits_total"
  comments_total ="comments_total"
  comments_no_auhtor = "comments_no_auhtor"
  bots_detected = "bots_detected"
  new_bots_detected = "new_bots_detected"
  new_users = "new_users"
  def __init__(self) -> None:
      super().__init__()
      self.create_category(self.subreddits_total, Total_Of_Incremnt_Data_Handler(message_end="subreddits have been crawled"))
      self.create_category(self.submissions_total,Total_Of_Incremnt_Data_Handler(message_end="submissions have been crawled"))
      self.create_category(self.comments_total,Total_Of_Incremnt_Data_Handler(message_end="comments have been crawled"))
      self.create_category(self.comments_no_auhtor, Total_Of_Incremnt_Data_Handler(message_end="comments have had no author"))
      self.create_category(self.bots_detected, Total_Of_Incremnt_Data_Handler(message_end="bots have been detected (not unique)"))
      self.create_category(self.new_bots_detected, Total_Of_Incremnt_Data_Handler(message_end="new bots have been detected"))
      self.create_category(self.new_users, Total_Of_Incremnt_Data_Handler(message_end="new users have been detected"))
  
  def increment_subreddits_total(self):
    self.update_value(self.subreddits_total,1)
  
  def accumulate_subreddit_data(self, subreddit_diagnostics: Subreddit_Crawl_Diagnostic):
    self.update_value(self.comments_total,subreddit_diagnostics.get(subreddit_diagnostics.comments_total))
    self.update_value(self.comments_no_auhtor,subreddit_diagnostics.get(subreddit_diagnostics.comments_no_auhtor))
    self.update_value(self.bots_detected,subreddit_diagnostics.get(subreddit_diagnostics.bots_detected))
    self.update_value(self.new_bots_detected,subreddit_diagnostics.get(subreddit_diagnostics.new_bots_detected))
    self.update_value(self.submissions_total,subreddit_diagnostics.get(subreddit_diagnostics.submissions_total))
    self.update_value(self.new_users,subreddit_diagnostics.get(subreddit_diagnostics.new_users))

  def log(self, logger: Logger):
    logger.log("-"*30)
    super().log(logger)
    logger.log("-"*30)