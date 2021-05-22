import sys
import data_util
import app_config
import data_saver
import simple_logging
import bot_blacklist
from time import sleep
import reddit_stream as rstr
import reddit_crawl as crawl
import visualize_data as vsd
import simple_logging
from simple_logging import Level, Logger
import data_generator as generator
import reddit_crawl_historical as rch
from cancel_token import Cancel_Token, Thread_Owned_Token_Tray
from subreddit import Subreddit_Batch_Queue
from bot_blacklist import Threadsafe_Bot_Blacklist
from defines import ACTIVE_KEYWORDS, ALL_ARGS, ALL_KEYWORD, BOT_LIST_FALLBACK, CRAWl_KEYWORDS,CRAWL_ARGS,GENERATE_ARGS, CONFIG, DATA_KEYWORDS, HISTORIC_CRAWL_KEYWORDS, START_KEYWORDS, STREAM_ARGS, HISTORIC_ARGS, STREAM_KEYWORDS, VISUALIZE_KEYWORDS, VIS_ARGS, EXIT_KEYWORDS

class FlowControl:
  crawl: bool
  generate: bool
  stream: bool
  historic_crawl:bool
  visualize:bool

  def __init__(self,crawl: bool, generate: bool, stream: bool, historic_crawl:bool,visualize:bool) -> None:
      self.crawl = crawl
      self.generate = generate
      self.stream = stream
      self.historic_crawl = historic_crawl
      self.visualize = visualize

def any_element_contained(args:list[str], check_against: list[str]) -> bool:
  return any(arg in args for arg in check_against)

def parse_args(args: list[str]) -> FlowControl:
  crawl = any_element_contained(args,CRAWL_ARGS)
  generate = any_element_contained(args,GENERATE_ARGS)
  stream = any_element_contained(args,STREAM_ARGS)
  historical = any_element_contained(args,HISTORIC_ARGS)
  visualize = any_element_contained(args,VIS_ARGS)
  if any_element_contained(args,ALL_ARGS):
    generate = True
    crawl = True
    stream = True
    historical = True
    visualize = True
  return FlowControl(crawl,generate, stream,historical,visualize)

def __get_bot_list_name(config: app_config.Config):
  blist_name = config.bot_list_name
  if blist_name == "":
    blist_name = BOT_LIST_FALLBACK
  return blist_name

def handle_observation_shut_down(config: app_config.Config,token: Cancel_Token, data_saver_tray: Thread_Owned_Token_Tray, logger: Logger, blist: Threadsafe_Bot_Blacklist, batch_queue: Subreddit_Batch_Queue):
  logger.log("Shutting Down - This may take some time",Level.INFO)
  logger.log("informing worker threads to cancel operations",Level.INFO)
  token.request_cancel()
  logger.log("waiting for worker threads to cancel",Level.INFO)
  token.wait()
  logger.log("finished waiting for worker threads",Level.INFO)
  logger.log("Saving data to disk",Level.INFO)      
  blist.save_to_file(__get_bot_list_name(config))
  
  data_saver_tray.try_rqeuest_cancel()
  data_saver_tray.try_wait()
  logger.log("Done with saving",Level.INFO)
  logger.stop()

def any_keyword_in_string(keywords: list[str], my_string:str):
  return any(keyword in my_string for keyword in keywords)

def print_help():
  print("To start anything start your command with one of these words {l}".format(l=START_KEYWORDS))
  print("Follow these up with a combination of the following:")
  print("\tTo start a crawl of reddit write {ck} and specifiy which with any of {t}".format(ck = CRAWl_KEYWORDS,t=list((ACTIVE_KEYWORDS,HISTORIC_CRAWL_KEYWORDS))))
  print("\tTo start the observation of reddit via a stream use any of {l}".format(l=STREAM_KEYWORDS))
  print("\tTo generate data use any of {l}".format(l=DATA_KEYWORDS))
  print("\tTo visualize data use any of{l}".format(l=VISUALIZE_KEYWORDS))
  print("To get help type help")
  print("To close the program use any of {l}".format(l = EXIT_KEYWORDS))

def handle_command(command, config: app_config.Config, logger:Logger, blist: Threadsafe_Bot_Blacklist,batch_queue: Subreddit_Batch_Queue,token: Cancel_Token) -> bool:
  if any_keyword_in_string(START_KEYWORDS,command):
    s_all = any_keyword_in_string(ALL_KEYWORD,command)
    did_something = False
    if s_all or any_keyword_in_string(CRAWl_KEYWORDS,command):
      if s_all or any_keyword_in_string(ACTIVE_KEYWORDS,command):
        crawl.run(config,logger,blist,batch_queue,token)
        did_something = True
      if s_all or any_keyword_in_string(HISTORIC_CRAWL_KEYWORDS,command):
        rch.run(config,logger,blist,batch_queue,token)
        did_something = True
    if s_all or any_keyword_in_string(STREAM_KEYWORDS, command):
      rstr.run(config,logger,blist,batch_queue,token)
      did_something = True
    if s_all or any_keyword_in_string(DATA_KEYWORDS,command):
      generator.run(config,logger,token)
      did_something = True
    if s_all or any_keyword_in_string(VISUALIZE_KEYWORDS,command):
      vsd.run(config,logger,token)
      did_something = True
    return did_something
  if "help" in command:
    print_help()
    return True
  return False

def print_not_understood(command: str):
  print("I didn't understand your command: '{c}'".format(c=command))
  print("Please try again (use help to list all commands)")

def main_observation_loop(config: app_config.Config,token: Cancel_Token,data_saver_tray: Thread_Owned_Token_Tray, batch_queue: Subreddit_Batch_Queue, blist: Threadsafe_Bot_Blacklist, logger: Logger):
    try:
      while True:
        inp = input("Command: ")
        if any(keyword in inp for keyword in EXIT_KEYWORDS):
          break
        if not handle_command(inp,config,logger,blist,batch_queue,token):
           print_not_understood(inp)
    finally:
      handle_observation_shut_down(config,token,data_saver_tray,logger,blist,batch_queue)


def run(program_flow: FlowControl, config: app_config.Config, logger: Logger):

  blist_name = __get_bot_list_name(config)

  blist: Threadsafe_Bot_Blacklist = bot_blacklist.load(blist_name)
  batch_queue: Subreddit_Batch_Queue = Subreddit_Batch_Queue()
  data_saver_tray = Thread_Owned_Token_Tray()
  token = Cancel_Token()

  data_saver.run(config,logger,batch_queue,data_saver_tray)

  if  program_flow.crawl:
    crawl.run(config, logger, blist, batch_queue,token)
  
  if program_flow.stream:
    rstr.run(config,logger,blist,batch_queue,token)

  if program_flow.historic_crawl:
    rch.run(config,logger,blist,batch_queue,token)

  if  program_flow.generate:
    generator.run(config, logger,token)

  if program_flow.visualize:
    vsd.run(config,logger,token)

  main_observation_loop(config,token,data_saver_tray,batch_queue,blist,logger)

  print("Goodbye!")


def main(args: list[str]):
  data_util.ensure_data_locations()
  config = app_config.load(CONFIG)
  logger: Logger = simple_logging.start(config.verbose,"Welcome Social Media Technologies 2021 Group 1")

  program_flow = parse_args(args)
  run(program_flow, config, logger)

if __name__ == "__main__":
  main(sys.argv)