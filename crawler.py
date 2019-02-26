import urllib.request as request
import bs4
import json
import operator
import re

def getBriefArticlesList(url, articlesNumber):
    getArticlesCount = 0
    pageCount = 1
    shouldContiune = True
    briefArticlesList = []

    while shouldContiune:
        html = getHTML(url+"&p="+str(pageCount))
        briefArticles = getBriefArticles(html)
        for article in briefArticles:
                briefArticlesList.append(article)
                getArticlesCount += 1
                if getArticlesCount >= articlesNumber:
                    shouldContiune = False
                    break
        pageCount+=1

    return briefArticlesList


def getHTML(url):
    with request.urlopen(url) as response:
        data = response.read().decode("utf-8")
        return data


def getBriefArticles(html):
    root = bs4.BeautifulSoup(html, "html.parser")
    articlesTitles = root.find_all("td", class_="subject")
    articlesReply = root.find_all("td", class_="reply")
    articlesUrl = root.find_all("td", class_="authur")

    briefArticlesList = []
    for i in range(len(articlesTitles)):
        title = articlesTitles[i].a.string
        reply = articlesReply[i].text
        href = articlesUrl[i].a["href"]
        briefArticlesList.append({"title":title, "reply": int(reply), "href": href})

    return briefArticlesList


def sortArticlesByReplies(articles):
    articles.sort(key = operator.itemgetter("reply"), reverse = True)
    return articles


def getDetailArticlesList(indexUrl, briefArticlesList):
    detailArticlesList = []
    # for briefArticle in briefArticlesList:
    #     detailArticle = getDetailArticle(indexUrl, briefArticle)
    #     detailArticlesList.append(detailArticle)

    briefArticle = briefArticlesList[0]
    detailArticle = getDetailArticle(indexUrl, briefArticle)
    detailArticlesList.append(detailArticle)
    
    return detailArticlesList


def getDetailArticle(indexUrl, briefArticle):
    html = getHTML(indexUrl + briefArticle["href"])
    article = getArticleInfo(html)
    replies = getArticleReplies(html)
    #article["replies": replies]
    return ""


def getArticleInfo(html):
    root = bs4.BeautifulSoup(html, "html.parser")
    Title = root.find("meta", property="og:title")["content"]
    InfoHTML = root.find("div", class_="single-post")
    authorId = InfoHTML.find("div", class_="fn").a.string
    popularity = int(InfoHTML.find("div", class_="info").text.replace("文章人氣: ", "").replace(",", ""))
    postTime = InfoHTML.find("div", class_="date").text.split("#")[0].replace(u'\xa0', u'')
    content = InfoHTML.find("div", class_="single-post-content").text

    return {"authorid": authorId, "title": Title, "popularity": popularity, "posttime": postTime, "content": content}


def getArticleReplies(indexHTML):
    root = bs4.BeautifulSoup(indexHTML, "html.parser")
    scripts = root.find_all("script", type="text/javascript")
    for script in scripts:
        if " maxpage" in script.text:
            print(script)

    return ""

def JsonWiter(message):
    print(json.dumps({"articles": message}, sort_keys=False, indent=4, ensure_ascii=False)) 