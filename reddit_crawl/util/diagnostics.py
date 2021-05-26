from utility.diagnostics import Timer_Data_Handler, Diagnostics, Counting_Data_Handler
from utility.simple_logging import Logger,Level
from enum import Enum
import time

class Subreddit_Timer_Data_Handler(Timer_Data_Handler):
  def __init__(self, diagnostic_parent) -> None:
      super().__init__()
      self.parent = diagnostic_parent

  def build_message(self, value):
    return "Crawl time for {n}: {t:0.4f} seconds".format(n=self.parent.name, t = self.seconds_passed(value))

class Total_Crawl_Time_Data_Handler(Timer_Data_Handler):
  def __init__(self) -> None:
      super().__init__()

  def log(self, value, logger: Logger):
    logger.log("Total crawl time: " + self.build_message(value),Level.INFO)
 

class RedditCrawlDiagnosticCategories(Enum):
  SUBMISSIONS_TOTAL = "submissions_total"
  COMMENTS_TOTAL ="comments_total"
  COMMENTS_NO_AUHTOR = "comments_no_auhtor"
  BOTS_DETECTED = "bots_detected"
  NEW_BOTS_DETECTED = "new_bots_detected"
  USERS_EXTRACTED = "users_extracted"
  TIME_ELAPSED= "time_elapsed"

class Reddit_Crawl_Diagnostics(Diagnostics):

  def __init__(self) -> None:
      super().__init__()
      self.create_category(RedditCrawlDiagnosticCategories.SUBMISSIONS_TOTAL.value,Counting_Data_Handler(message_end="submissions have been crawled"))
      self.create_category(RedditCrawlDiagnosticCategories.COMMENTS_TOTAL.value,Counting_Data_Handler(message_end="comments have been crawled"))
      self.create_category(RedditCrawlDiagnosticCategories.COMMENTS_NO_AUHTOR.value, Counting_Data_Handler(message_end="comments have had no author"))
      self.create_category(RedditCrawlDiagnosticCategories.BOTS_DETECTED.value, Counting_Data_Handler(message_end="bots have been detected (not unique)"))
      self.create_category(RedditCrawlDiagnosticCategories.NEW_BOTS_DETECTED.value, Counting_Data_Handler(message_end="new bots have been detected"))
      self.create_category(RedditCrawlDiagnosticCategories.USERS_EXTRACTED.value, Counting_Data_Handler(message_end="users have been detected"))
      self.create_category(RedditCrawlDiagnosticCategories.TIME_ELAPSED.value, Total_Crawl_Time_Data_Handler())
  
  def increment_comments_total(self):
    self.update_value(RedditCrawlDiagnosticCategories.COMMENTS_TOTAL.value,1)

  def increment_usrers_extracted_total(self):
    self.update_value(RedditCrawlDiagnosticCategories.USERS_EXTRACTED.value,1) 

  def increment_comments_no_author(self):
    self.update_value(RedditCrawlDiagnosticCategories.COMMENTS_NO_AUHTOR.value,1)

  def increment_bots_detected(self):
    self.update_value(RedditCrawlDiagnosticCategories.BOTS_DETECTED.value,1)

  def increment_submission_total(self):
    self.update_value(RedditCrawlDiagnosticCategories.SUBMISSIONS_TOTAL.value,1)

  def increment_new_bots_total(self):
    self.update_value(RedditCrawlDiagnosticCategories.NEW_BOTS_DETECTED.value,1)

  def update_timing(self):
    self.update_value(RedditCrawlDiagnosticCategories.TIME_ELAPSED.value,None)

  def end_timing(self):
    self.update_value(RedditCrawlDiagnosticCategories.TIME_ELAPSED.value,None)

  def reset_timing(self):
    self.reset_value(RedditCrawlDiagnosticCategories.TIME_ELAPSED.value)

  def log(self, logger: Logger):
    s ="-"*15 + "Total Crawl" + "-"*15+"\n"
    s+= super().to_string()
    s+="-"*30
    logger.log(s,Level.INFO)