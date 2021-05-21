#reddit info
CLIENT_ID="oLm5KqTNCR5qrw"
CLIENT_SECRET="E-uXbSsa6JTNph_zp49vnbSLZpO0tg"
USER_AGENT="python:TUG-CommentCrawler:v1.0.0 (by u/Ignaz503)"

#args
CRAWL_ARGS = ["-crawl","-c"]
GENERATE_ARGS = ["-generate","-g"]
ALL_ARGS = ["-all","-a", "-both"]
STREAM_ARGS = ["-s","-str", "-stream"]
HISTORIC_ARGS = ["-h","-historic","-hc","-historic-crawl","-ch"]
VIS_ARGS = ["-v","-vis","-visualize"]

#keyworkds
EXIT_KEYWORDS =["stop","exit","end", "kill", "terminate"]
START_KEYWORDS=["start","engage", "kick off", "run", "do", "observe", "monitor", "create"]
CRAWl_KEYWORDS = ["crawl"]
HISTORIC_CRAWL_KEYWORDS = ["historic", "h", "old"]
ACTIVE_KEYWORDS = ["active", "repeated"]
STREAM_KEYWORDS = ["stream", "stream observation"]
GENERATE_KEYWORDS =["generate", "gen"]
VISUALIZE_KEYWORDS = ["visualize", "vis", "visualization"]
ALL_KEYWORD = ["all"]

#time
MIN_REPEAT_TIME = 5 * 60

#filenames
ADJACENCY_MAT = "mat.csv"
CONFIG = "app.config"
BOT_LIST_FALLBACK = "bot_list.json"
