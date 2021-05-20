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

#time
MIN_REPEAT_TIME = 5 * 60

#filenames
ADJACENCY_MAT = "mat.csv"
CONFIG = "app.config"
BOT_LIST_FALLBACK = "bot_list.json"
