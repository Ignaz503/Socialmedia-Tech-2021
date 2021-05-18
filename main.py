from os import path
import os
from submission_getters import NewSubmissionGetter
from time import sleep
import app_config
import sys
import reddit_crawl as crawl
import data_generator as generator
from simple_logging import Logger
from defines import ALL_ARGS, DATA_BASE_PATH,CRAWL_ARGS,GENERATE_ARGS, MIN_REPEAT_TIME, REPEAT_ARGS
from repeated_timer import RepeatedTimer

def ensure_data_location():
  if not path.exists(DATA_BASE_PATH):
    os.makedirs(DATA_BASE_PATH)

def any_element_contained(args:list[str], check_against: list[str]) -> bool:
  return any(arg in args for arg in check_against)

def parse_args(args: list[str]) -> tuple[bool,bool,bool]:
  crawl = any_element_contained(args,CRAWL_ARGS)
  generate = any_element_contained(args,GENERATE_ARGS)
  repeat = any_element_contained(args,REPEAT_ARGS)
  if any_element_contained(args,ALL_ARGS):
    generate = True
    crawl = True
  return (crawl,generate, repeat)

def just_crawl(config: app_config.Config, logger: Logger):
  crawl.run(config, logger)

def just_generate(config: app_config.Config, logger: Logger):
  generator.run(config,logger)

def crawl_and_generate(config: app_config.Config, logger:Logger):
  crawl.run(config,logger)
  generator.run(config,logger)

def handle_repeat_execution(config: app_config.Config, logger: Logger,  to_execute: tuple[bool,bool,bool]):
  #todo config time reading
  seconds = config.get_repeat_time_in_seconds()

  if seconds < MIN_REPEAT_TIME:
    logger.log("can't repeat faster than {rpt}".format(rpt= MIN_REPEAT_TIME))
    seconds = MIN_REPEAT_TIME

  max_repetitions = config.max_repetitions
  function = just_crawl

  if to_execute[0] and to_execute[1]:
    logger.log("crawling and generating every {t} seconds up to a max of {r} repetitions".format(t = seconds, r = max_repetitions))
    function = crawl_and_generate
  elif to_execute[0]:
    logger.log("crawling every {t} seconds up to a max of {r} repetitions".format(t = seconds, r = max_repetitions))
    function = just_crawl
  elif to_execute[1]:
    logger.log("generating every {t} seconds up to a max of {r} repetitions".format(t = seconds, r = max_repetitions))
    function = just_generate
  else:
    logger.log("nothing is repeated")
    return # we are not doing anything
  repeater = RepeatedTimer(seconds,max_repetitions,function,config,logger)
  try:
    logger.log("waiting for repetitions to end (stop it with a keyboard interrupt)")
    repeater.start()
    sleep(seconds*max_repetitions)
  except KeyboardInterrupt:
    repeater.stop()


def main(args: list[str]):
  ensure_data_location()
  config = app_config.load(app_config.FILE)
  logger: Logger = Logger(config.verbose)

  to_execute = parse_args(args)

  if  to_execute[0]:
    crawl.run(config, logger)

  if  to_execute[1]:
    generator.run(config, logger)

  if to_execute[2]:
    handle_repeat_execution(config, logger, to_execute)
  

if __name__ == "__main__":
  main(sys.argv)