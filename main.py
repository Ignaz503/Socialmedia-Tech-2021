from cancel_token import Cancel_Token
from os import path
import os
from subreddit import Subreddit_Batch_Queue
from time import sleep
import app_config
import sys
import reddit_crawl as crawl
import data_generator as generator
from simple_logging import Logger
from defines import ALL_ARGS, BOT_LIST, DATA_BASE_PATH,CRAWL_ARGS,GENERATE_ARGS, MIN_REPEAT_TIME, CONFIG, STREAM_ARGS
from repeated_timer import RepeatedTimer
import bot_blacklist
from bot_blacklist import Threadsafe_Bot_Blacklist
import reddit_stream as rstr

def ensure_data_location():
  if not path.exists(DATA_BASE_PATH):
    os.makedirs(DATA_BASE_PATH)

def any_element_contained(args:list[str], check_against: list[str]) -> bool:
  return any(arg in args for arg in check_against)

def parse_args(args: list[str]) -> tuple[bool,bool,bool]:
  crawl = any_element_contained(args,CRAWL_ARGS)
  generate = any_element_contained(args,GENERATE_ARGS)
  stream = any_element_contained(args,STREAM_ARGS)
  if any_element_contained(args,ALL_ARGS):
    generate = True
    crawl = True
    stream = True
  return (crawl,generate, stream)

def just_crawl(config: app_config.Config, logger: Logger, batch_queue: Subreddit_Batch_Queue):
  crawl.run(config, logger, batch_queue)

def handle_repeat_execution(config: app_config.Config, logger: Logger, batch_queue: Subreddit_Batch_Queue, to_execute: tuple[bool,bool,bool]) -> RepeatedTimer:
  #todo config time reading
  seconds = config.get_repeat_time_in_seconds()

  if seconds == 0:
    return None

  if seconds < MIN_REPEAT_TIME:
    seconds = MIN_REPEAT_TIME

  repeater = RepeatedTimer(seconds,just_crawl,config,logger,batch_queue)
  repeater.start()
  return repeater


def handle_observation_shut_down(repeat_action: RepeatedTimer, tokens:tuple[Cancel_Token,Cancel_Token], logger: Logger, blist: Threadsafe_Bot_Blacklist, batch_queue: Subreddit_Batch_Queue):
  logger.log("Shutting Down Data Gathering - This may take some time")
  if repeat_action is not None:
    repeat_action.stop()
  if tokens is not None:
    tokens[0].request_cancel()
    tokens[1].request_cancel()
    logger.log("Waiting for streams to end")
    tokens[0].wait()
    tokens[1].wait()
    logger.log("Streams ended")
  logger.log("Saving data to disk")      
  blist.save_to_file(BOT_LIST)
  batch_queue.handle_all(logger)
  logger.log("Done with saving")

def main(args: list[str]):
  ensure_data_location()
  config = app_config.load(CONFIG)
  logger: Logger = Logger(config.verbose)
  blist: Threadsafe_Bot_Blacklist = bot_blacklist.load(BOT_LIST)
  batch_queue: Subreddit_Batch_Queue = Subreddit_Batch_Queue()

  to_execute = parse_args(args)

  repeat_action = None
  if  to_execute[0]:
    crawl.run(config, logger, blist, batch_queue)
    repeat_action = handle_repeat_execution(config, logger, blist, to_execute)
  
  tokens: tuple[Cancel_Token,Cancel_Token] = None
  if to_execute[2]:
    tokens = rstr.run(config,logger,blist,batch_queue)

  while True:
    try:
      batch_queue.update(logger)
      sleep(config.batch_save_interval_seconds)
    except KeyboardInterrupt:
      handle_observation_shut_down(repeat_action,tokens,logger,blist,batch_queue)
      break

  if  to_execute[1]:
    generator.run(config, logger)

  print("Goodbye!")


if __name__ == "__main__":
  main(sys.argv)