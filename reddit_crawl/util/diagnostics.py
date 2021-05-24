from utility.diagnostics import Timer_Data_Handler, Diagnostics, Total_Of_Incremnt_Data_Handler
from utility.simple_logging import Logger,Level

class Subreddit_Timer_Data_Handler(Timer_Data_Handler):
  def __init__(self, diagnostic_parent) -> None:
      super().__init__()
      self.parent = diagnostic_parent

  def build_message(self, value):
    return "Crawl time for {n}: {t:0.4f} seconds".format(n=self.parent.name, t = self.seconds_passed(value))

class Total_Crawl_Time_Data_Handler(Timer_Data_Handler):
  def __init__(self) -> None:
      super().__init__()
  def build_message(self, value):
    return "Total crawling time: {t:0.4f} seconds".format(t = self.seconds_passed(value))

class Reddit_Crawl_Diagnostics(Diagnostics):
  submissions_total = "submissions_total"
  comments_total ="comments_total"
  comments_no_auhtor = "comments_no_auhtor"
  bots_detected = "bots_detected"
  new_bots_detected = "new_bots_detected"
  users_extracted = "users_extracted"
  time_elapsed="time_elapsed"
  def __init__(self) -> None:
      super().__init__()
      self.create_category(self.submissions_total,Total_Of_Incremnt_Data_Handler(message_end="submissions have been crawled"))
      self.create_category(self.comments_total,Total_Of_Incremnt_Data_Handler(message_end="comments have been crawled"))
      self.create_category(self.comments_no_auhtor, Total_Of_Incremnt_Data_Handler(message_end="comments have had no author"))
      self.create_category(self.bots_detected, Total_Of_Incremnt_Data_Handler(message_end="bots have been detected (not unique)"))
      self.create_category(self.new_bots_detected, Total_Of_Incremnt_Data_Handler(message_end="new bots have been detected"))
      self.create_category(self.users_extracted, Total_Of_Incremnt_Data_Handler(message_end="users have been detected"))
      self.create_category(self.time_elapsed, Total_Crawl_Time_Data_Handler())
  
  def increment_comments_total(self):
    self.update_value(self.comments_total,1) 
  
  def increment_usrers_extracted_total(self):
    self.update_value(self.users_extracted,1) 

  def increment_comments_no_author(self):
    self.update_value(self.comments_no_auhtor,1)
  
  def increment_bots_detected(self):
    self.update_value(self.bots_detected,1)
  
  def increment_submission_total(self):
    self.update_value(self.submissions_total,1)
  
  def increment_new_bots_total(self):
    self.update_value(self.new_bots_detected,1)

  def end_timing(self):
    self.update_value(self.time_elapsed,None)

  def log(self, logger: Logger):
    s ="-"*15 + "Total Crawl" + "-"*15+"\n"
    s+= super().to_string()
    s+="-"*30
    logger.log(s,Level.INFO)