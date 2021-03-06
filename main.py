import sys
import utility.data_util as data_util
from utility.app_config import Config
import reddit_crawl.util.subreddit_batch_queue_data_saver as data_saver
import utility.simple_logging as simple_logging
import reddit_crawl.data.bot_blacklist as bot_blacklist
import reddit_crawl.stream_observation as rstr
import reddit_crawl.active_crawl as crawl
import generators.visualization_generator as vsd
from utility.simple_logging import Logger, Level
import generators.data_generator as generator
import reddit_crawl.historical_crawl as rch
from utility.cancel_token import Cancel_Token, Thread_Owned_Token_Tray
from reddit_crawl.data.subreddit import Subreddit_Batch_Queue
from reddit_crawl.data.bot_blacklist import Threadsafe_Bot_Blacklist
from defines import ACTIVE_KEYWORDS, ALL_ARGS, ALL_KEYWORD, BOT_LIST_FALLBACK, CRAWl_KEYWORDS,CRAWL_ARGS,GENERATE_ARGS, CONFIG, DATA_KEYWORDS, HISTORIC_CRAWL_KEYWORDS, START_KEYWORDS, STREAM_ARGS, HISTORIC_ARGS, STREAM_KEYWORDS, VISUALIZE_KEYWORDS, VIS_ARGS, EXIT_KEYWORDS

__data_processing_was_run: bool = False

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

def __set_data_processing_run_flag(value: bool = True):
  global __data_processing_was_run
  __data_processing_was_run = value

def handle_observation_shut_down(config: Config,token: Cancel_Token, data_saver_tray: Thread_Owned_Token_Tray, logger: Logger, blist: Threadsafe_Bot_Blacklist, batch_queue: Subreddit_Batch_Queue):
  logger.log("Shutting Down - This may take some time",Level.INFO)
  logger.log("informing worker threads to cancel operations",Level.INFO)
  token.request_cancel()
  logger.log("waiting for worker threads to cancel",Level.INFO)
  token.wait()
  logger.log("finished waiting for worker threads",Level.INFO)
  logger.log("Saving data to disk",Level.INFO)      
  blist.save_to_file(config.get_bot_list_name(),config)
  
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

def handle_command(command, config: Config, logger:Logger, blist: Threadsafe_Bot_Blacklist,batch_queue: Subreddit_Batch_Queue,token: Cancel_Token) -> bool:
  global __data_processing_was_run
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
      generator.run(config,logger,token,lambda: __set_data_processing_run_flag())
      did_something = True
    if s_all or any_keyword_in_string(VISUALIZE_KEYWORDS,command):
      vsd.run(config,logger,token, __data_processing_was_run)
      did_something = True
    return did_something
  if "help" in command:
    print_help()
    return True

  return False

def print_not_understood(command: str):
  print("I didn't understand your command: '{c}'".format(c=command))
  print("Please try again (use help to list all commands)")

def main_observation_loop(config: Config,token: Cancel_Token,data_saver_tray: Thread_Owned_Token_Tray, batch_queue: Subreddit_Batch_Queue, blist: Threadsafe_Bot_Blacklist, logger: Logger):
    try:
      while True:
        inp = input("Command: ")
        if any(keyword in inp for keyword in EXIT_KEYWORDS):
          break
        if not handle_command(inp,config,logger,blist,batch_queue,token):
           print_not_understood(inp)
    finally:
      handle_observation_shut_down(config,token,data_saver_tray,logger,blist,batch_queue)

def run(program_flow: FlowControl, config: Config, logger: Logger):
  global __data_processing_was_run

  blist_name = config.get_bot_list_name()

  blist: Threadsafe_Bot_Blacklist = bot_blacklist.load(blist_name,config)
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
    generator.run(config, logger,token,lambda: __set_data_processing_run_flag())

  if program_flow.visualize:
    vsd.run(config,logger,token,__data_processing_was_run)

  main_observation_loop(config,token,data_saver_tray,batch_queue,blist,logger)

  print("Goodbye!")

def main(args: list[str]):
  config = Config.load(CONFIG)
  data_util.ensure_data_locations(config)
  logger: Logger = simple_logging.start(config)

  program_flow = parse_args(args)
  run(program_flow, config, logger)

if __name__ == "__main__":
  main(sys.argv)