from os import path
import os
import app_config
import sys
import reddit_crawl as crawl
import data_generator as generator
from simple_logging import Logger
import defines
from defines import ALL_ARGS, DATA_BASE_PATH,CRAWL_ARGS,GENERATE_ARGS

def ensure_data_location():
  if not path.exists(DATA_BASE_PATH):
    os.makedirs(DATA_BASE_PATH)

def parse_args(args: list[str]) -> tuple[bool,bool]:
  crawl = any(arg in args for arg in CRAWL_ARGS)
  generate = any(arg in args for arg in GENERATE_ARGS)
  if any(arg in args for arg in ALL_ARGS):
    generate = True
    crawl = True
  return (crawl,generate)


def main(args: list[str]):
  ensure_data_location()
  config = app_config.load(app_config.FILE)
  logger: Logger = Logger(config.verbose)

  to_execute = parse_args(args)

  if  to_execute[0]:
    crawl.run(config, logger)

  if  to_execute[1]:
    generator.run(config, logger)


if __name__ == "__main__":
  main(sys.argv)