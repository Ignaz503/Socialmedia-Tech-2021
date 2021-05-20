import sys
import data_util
import app_config
import bot_blacklist
from time import sleep
import reddit_stream as rstr
import reddit_crawl as crawl
import visualize_data as vsd
from simple_logging import Logger
import data_generator as generator
import reddit_crawl_historical as rch
from cancel_token import Cancel_Token
from subreddit import Subreddit_Batch_Queue
from bot_blacklist import Threadsafe_Bot_Blacklist
from defines import ALL_ARGS, BOT_LIST_FALLBACK,CRAWL_ARGS,GENERATE_ARGS, CONFIG, STREAM_ARGS, HISTORIC_ARGS, VIS_ARGS

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

  def need_to_run_main_observation_loop(self)-> bool:
    return self.crawl or self.stream or self.historic_crawl


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

def handle_observation_shut_down(crawl_token: Cancel_Token, tokens:tuple[Cancel_Token,Cancel_Token], logger: Logger, blist: Threadsafe_Bot_Blacklist, batch_queue: Subreddit_Batch_Queue):
  logger.log("Shutting Down Data Gathering - This may take some time")
  if crawl_token is not None:
    crawl_token.request_cancel()
    crawl_token.wait()
  if tokens is not None:
    tokens[0].request_cancel()
    tokens[1].request_cancel()
    logger.log("Waiting for streams to end")
    tokens[0].wait()
    tokens[1].wait()
    logger.log("Streams ended")
  logger.log("Saving data to disk")      
  blist.save_to_file(BOT_LIST_FALLBACK)
  batch_queue.handle_all(logger)
  logger.log("Done with saving")

def main_observation_loop(config: app_config.Config,crawl_token: Cancel_Token,tokens: tuple[Cancel_Token,Cancel_Token],batch_queue: Subreddit_Batch_Queue, blist: Threadsafe_Bot_Blacklist, logger: Logger):
    while True:
      try:
        batch_queue.update(logger)
        sleep(config.batch_save_interval_seconds)
      except KeyboardInterrupt:
        handle_observation_shut_down(crawl_token,tokens,logger,blist,batch_queue)
        break

def run(program_flow: FlowControl, config: app_config.Config, logger: Logger):

  blist_name = config.bot_list_name
  if blist_name == "":
    blist_name = BOT_LIST_FALLBACK

  blist: Threadsafe_Bot_Blacklist = bot_blacklist.load(blist_name)
  batch_queue: Subreddit_Batch_Queue = Subreddit_Batch_Queue()

  crawl_token: Cancel_Token = None
  if  program_flow.crawl:
    crawl_token = crawl.run(config, logger, blist, batch_queue)
  
  tokens: tuple[Cancel_Token,Cancel_Token] = None
  if program_flow.stream:
    tokens = rstr.run(config,logger,blist,batch_queue)

  if program_flow.historic_crawl:
    rch.run(config,logger,blist,batch_queue)

  #only run if eiter of stream 
  if program_flow.need_to_run_main_observation_loop():
    logger.log("starting batch queue loop")
    main_observation_loop(config,crawl_token,tokens,batch_queue,blist,logger)

  if  program_flow.generate:
    generator.run(config, logger)

  if program_flow.visualize:
    vsd.run(config,logger)

  logger.log("Goodbye!")


def main(args: list[str]):
  data_util.ensure_data_locations()
  config = app_config.load(CONFIG)
  logger: Logger = Logger(config.verbose)

  program_flow = parse_args(args)
  run(program_flow, config, logger)

if __name__ == "__main__":
  main(sys.argv)