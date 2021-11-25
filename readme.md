# Social Media Technologies 2021 Group 1

This applet crawls user defined subreddits and extracts information such as which user posted/comment in the subreddits I am interessted in.
This information can afterwards be visualized in a few ways to analyze the data found.
The visualizations are output as html file.
For large datasets it is recommended to use the also generated DOT files and a external Tool like [Gephi](https://gephi.org/)

run python main.py [Args] to run the command line tool
run pythin application.py to get a GUI

## Running the program

Before you run the program ensure these things are installed:

- [python](https://www.python.org/downloads/release/python-395/)
- [praw](https://praw.readthedocs.io/en/latest/)
- [psaw](https://psaw.readthedocs.io/en/latest/)
- [jsonpickle](https://jsonpickle.github.io/)
- [numpy](https://numpy.org/)
- [networkx](https://networkx.org/documentation/stable/index.html)
- [pyvis](https://pyvis.readthedocs.io/en/latest/index.html)
- [pygraphviz](https://pygraphviz.github.io/documentation/stable/install.html)
- [colour](https://pypi.org/project/colour/)

## Reddit App

To be able to crawl reddit at all you need to create and app and accept reddits API terms

- [Reddit App](https://www.reddit.com/prefs/apps)
- [Reddit API Terms](https://docs.google.com/forms/d/e/1FAIpQLSezNdDNK1-P8mspSbmtC2r86Ee9ZRbC66u929cG2GX0T9UMyw/viewform)

Once your app is registered update the config file with your cleint ID and client secret
as well as the user agent (how this should look like is explained [here](https://github.com/reddit-archive/reddit/wiki/API))
