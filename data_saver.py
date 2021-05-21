from subreddit import Subreddit_Batch_Queue
from app_config import Config
from simple_logging import Logger
from cancel_token import Thread_Owned_Token_Tray, Thread_Owned_Cancel_Token
import time
import threading

def __execute_save_loop(config: Config, logger: Logger,batch_queue: Subreddit_Batch_Queue, tray: Thread_Owned_Token_Tray):
  token: Thread_Owned_Cancel_Token = Thread_Owned_Cancel_Token()
  tray.set_token(token)
  with token:
    current_time = time.time()
    last_execution =  current_time # start sleeping
    while not token.is_cancel_requested():
      if current_time - last_execution >= config.batch_save_interval_seconds:
        last_execution = current_time
        batch_queue.update(logger)
      current_time = time.time()
    batch_queue.handle_all(logger)

def run(config: Config, logger: Logger,batch_queue: Subreddit_Batch_Queue, tray: Thread_Owned_Token_Tray):
  thread = threading.Thread(name="data saver", target=__execute_save_loop,args=(config,logger,batch_queue,tray))
  thread.start()