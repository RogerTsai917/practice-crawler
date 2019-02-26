import crawler
import bs4

indexUrl = "https://www.mobile01.com/"
url = "https://www.mobile01.com/topiclist.php?f=383"
articlesNumber = 35

briefArticlesList = crawler.getBriefArticlesList(url, articlesNumber)

briefArticlesList = crawler.sortArticlesByReplies(briefArticlesList)

articlesList = crawler.getDetailArticlesList(indexUrl, briefArticlesList)