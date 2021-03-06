#reddit application info
CLIENT_ID='client_id'
CLIENT_SECRET='client_secret'
USER_AGENT='user_agent'
USE_USER_ACCOUNT= 'use_user_account'
USER_ACCOUNT_NAME= 'user_account_name'
USER_ACCOUNT_PWD = 'user_account_password'
REDIRECT_URI ='redirect_uri'

#submission getter dict entry
GETTER_TYPE = 'type'
GETTER_CATEGORY = 'category'

#args
CRAWL_ARGS = ["-crawl","-c"]
GENERATE_ARGS = ["-generate","-g"]
ALL_ARGS = ["-all","-a", "-both"]
STREAM_ARGS = ["-s","-str", "-stream"]
HISTORIC_ARGS = ["-h","-historic","-hc","-historic-crawl","-ch"]
VIS_ARGS = ["-v","-vis","-visualize"]

#keyworkds
EXIT_KEYWORDS =["stop","exit","end", "kill", "terminate"]
START_KEYWORDS=["start","engage", "kick off", "run", "do", "observe", "monitor", "create", "generate"]
CRAWl_KEYWORDS = ["crawl"]
HISTORIC_CRAWL_KEYWORDS = ["historic", "h", "old"]
ACTIVE_KEYWORDS = ["active", "repeated"]
STREAM_KEYWORDS = ["stream", "stream observation"]
DATA_KEYWORDS =["data", "metadata", "meta"]
VISUALIZE_KEYWORDS = ["visualize", "vis", "visualization"]
ALL_KEYWORD = ["all"]

#crawl defines
MIN_REPEAT_TIME = 5 * 60
MIN_BATCH_SAVE_TIME = 5
MAX_COMMENT_NUM = 1000

#filenames
CONFIG = "app.config"
BOT_LIST_FALLBACK = "bot_list.json"

#log defines
MAX_NUM_ROWS = 200

#max subreddit group size in bytes
MAX_SIZE_BYTES = 20*1024*1024 #20MB