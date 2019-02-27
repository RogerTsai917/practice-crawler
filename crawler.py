import urllib.request as request
import bs4
import json
import operator
import re
import time

def getBriefArticlesList(url, articlesNumber):
    print("Search " + str(articlesNumber) + " articles")
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
    time.sleep(1)
    with request.urlopen(url) as response:
        data = response.read().decode("utf-8")
        return data


def getBriefArticles(html):
    root = bs4.BeautifulSoup(html, "lxml")
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
    articlesCount = 1
    for briefArticle in briefArticlesList:
        detailArticle = getDetailArticle(indexUrl, briefArticle)
        detailArticlesList.append(detailArticle)
        print("finished " + str(articlesCount) + " / " + str(len(briefArticlesList)))
        articlesCount += 1
    
    return detailArticlesList


def getDetailArticle(indexUrl, briefArticle):
    html = getHTML(indexUrl + briefArticle["href"])
    article = getArticleInfo(html)
    replies = getAllArticleReplies(html, indexUrl + briefArticle["href"])
    article["replies"] = replies
    return article


def getArticleInfo(html):
    root = bs4.BeautifulSoup(html, "lxml")
    Title = root.find("meta", property="og:title")["content"]
    InfoHTML = root.find("div", class_="single-post")
    authorId = InfoHTML.find("div", class_="fn").a.string
    popularity = InfoHTML.find("div", class_="info").text.replace("文章人氣: ", "").replace(",", "")
    if popularity == " ":
        popularity = 0
    else:
        popularity = int(popularity)
    postTime = InfoHTML.find("div", class_="date").text.split("#")[0].replace(u'\xa0', u'')
    content = InfoHTML.find("div", class_="single-post-content").text

    return {"authorid": authorId, "title": Title, "popularity": popularity, "posttime": postTime, "content": content}


def getAllArticleReplies(indexHTML, indexUrl):
    root = bs4.BeautifulSoup(indexHTML, "lxml")
    maxPage = getMaxPage(root)
    AllArticleReplies = []
    for page in range(1, maxPage + 1):
        url = indexUrl + "&p=" + str(page)
        onePageReplies = getOnePageReplies(url)
        AllArticleReplies.extend(onePageReplies)
    return AllArticleReplies


def getOnePageReplies(url):
    onePageReplies = []
    html = getHTML(url)
    root = bs4.BeautifulSoup(html, "lxml")
    replies = root.find_all("div", class_="single-post")
    for replie in replies:
        if replie.find("div", class_="info").text == " ":
            authorId = replie.find("div", class_="fn").a.string
            postTime = replie.find("div", class_="date").text.split("#")[0].replace(u'\xa0', u'')
            contentHTML = replie.find("div", class_="single-post-content")
            blockquote = contentHTML.find("blockquote")
            if blockquote:
                contentHTML.blockquote.decompose()
            content = contentHTML.text
            onePageReplies.append({"authorid": authorId, "posttime": postTime, "content": content})
    return onePageReplies

def getMaxPage(root):
    pattern = re.compile(r'maxpage = (\d+)')
    scripts = root.find_all("script", text=pattern)
    maxpage = 1
    for script in scripts:
        maxpage = int(pattern.search(script.text).group(1))
    return maxpage


def JsonWiter(message):
    with open('articles.json', 'w', encoding='utf-8') as outfile:
        json.dump(message, outfile, ensure_ascii=False, indent=4)