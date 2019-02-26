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
    replies = getArticleReplies(html, indexUrl + briefArticle["href"])
    print(replies)
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


def getArticleReplies(indexHTML, indexUrl):
    root = bs4.BeautifulSoup(indexHTML, "html.parser")
    maxPage = getMaxPage(root)
    ArticleReplies = []
    for page in range(1, 2):
        html = getHTML(indexUrl + "&p=" + str(page))
        root = bs4.BeautifulSoup(html, "html.parser")
        replies = root.find_all("div", class_="single-post")
        for replie in replies:
            if replie.find("div", class_="info").text == " ":
                authorId = replie.find("div", class_="fn").a.string
                postTime = replie.find("div", class_="date").text.split("#")[0].replace(u'\xa0', u'')
                content = replie.find("div", class_="single-post-content").text
                ArticleReplies.append({"authorid": authorId, "posttime": postTime, "content": content})

    return ArticleReplies

def getMaxPage(root):
    pattern = re.compile(r'maxpage = (\d+)')
    scripts = root.find_all("script", text=pattern)
    maxpage = 1
    for script in scripts:
        maxpage = int(pattern.search(script.text).group(1))
    return maxpage


def JsonWiter(message):
    print(json.dumps({"articles": message}, sort_keys=False, indent=4, ensure_ascii=False)) 