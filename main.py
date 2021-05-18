from os import path
import os
import app_config
import sys
import reddit_crawl as crawl
import data_generator as generator
from simple_logging import Logger
import defines


def ensure_data_location():
  if not path.exists(defines.DATA_BASE_PATH):
    os.makedirs(defines.DATA_BASE_PATH)

def main(args: list[str]):
  ensure_data_location()
  config = app_config.load(app_config.FILE)
  logger: Logger = Logger(config.verbose)
  if "-crawl" in args:
    crawl.run(config, logger)

  if "-generate" in args:
    generator.run(config, logger)


if __name__ == "__main__":
  main(sys.argv)