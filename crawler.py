import urllib.request as request
import bs4
import json
import operator
import re
import time

def getBriefArticlesList(url, articlesNumber):
    print("Search " + str(articlesNumber) + " articles")
    # 用來計算已獲取的文章數
    getArticlesCount = 0
    # 從討論版的第一頁開始計算
    pageCount = 1 
    shouldContiune = True
    # 要回傳的基本文章 List
    briefArticlesList = []

    while shouldContiune:
        # 呼叫 getOnePageBriefArticles(url) 獲得單頁的基本文章表
        briefArticles = getOnePageBriefArticles(url+"&p="+str(pageCount))
        # 把獲得單頁的基本文章表加到要回傳的 briefArticlesList，
        # 如果文章數到達需求書量就跳出迴圈
        for article in briefArticles:
                briefArticlesList.append(article)
                getArticlesCount += 1
                if getArticlesCount >= articlesNumber:
                    shouldContiune = False
                    break
        # 如果此頁的文章加總不足需求數，就會跳下一頁
        pageCount+=1

    return briefArticlesList


# 獲得單頁的基本文章列表
def getOnePageBriefArticles(url):
    # 透過 getHTML(url) 拿到目標網址的 HTML檔
    html = getHTML(url)
    # 把 html 傳給 BeautifulSoup 即可用解析網頁碼
    # lxml 則是用來作為 BeautifulSoup 的解析器，還有 html.parser 與 html5lib等
    # 根據官方文件的推薦，我使用解析速度最快的 lxml
    root = bs4.BeautifulSoup(html, "lxml")
    # 獲得所有文章的標題、回覆數和 Url
    articlesTitles = root.find_all("td", class_="subject")
    articlesReply = root.find_all("td", class_="reply")
    articlesUrl = root.find_all("td", class_="authur")

    briefArticlesList = []
    # 依序填入到 briefArticlesList中
    for i in range(len(articlesTitles)):
        title = articlesTitles[i].a.string
        reply = articlesReply[i].text
        href = articlesUrl[i].a["href"]
        briefArticlesList.append({"title":title, "reply": int(reply), "href": href})

    # 回傳單頁文章基本列表 briefArticlesList
    return briefArticlesList


def getHTML(url):
    # 每次請求之前先暫停1秒，以免連續請求被伺服器拒絕
    time.sleep(1)
    # 透過 urllib.request.urlopen(url) 可以拿到網址的請求資料
    with request.urlopen(url) as response:
        # 並免亂碼，所以要用 utf-8解碼
        data = response.read().decode("utf-8")
        # 回傳HTML
        return data


# 根據回覆數量排序文章列表
def sortArticlesByReplies(articles):
    # 根據 key = "reply"的 value做排序
    # reverse = True:降序，reverse = False:升序(默認)
    articles.sort(key = operator.itemgetter("reply"), reverse = True)
    return articles


# 根據基本文章列表，獲得所有文章的詳細內容
def getDetailArticlesList(indexUrl, briefArticlesList):
    detailArticlesList = []
    articlesCount = 1

    # 把每篇文章傳到 getDetailArticle獲得文章的詳細內容，
    # 並每篇文章加到 detailArticlesList
    for briefArticle in briefArticlesList:
        detailArticle = getDetailArticle(indexUrl, briefArticle)
        detailArticlesList.append(detailArticle)
        # 用來顯示已爬完成幾篇文章
        print("finished " + str(articlesCount) + " / " + str(len(briefArticlesList)))
        articlesCount += 1
    # 回傳 detailArticlesList
    return detailArticlesList


# 獲得單一文章的詳細內容
def getDetailArticle(indexUrl, briefArticle):
    # 透過 getHTML(url) 拿到目標文章的 HTML檔
    html = getHTML(indexUrl + briefArticle["href"])
    # article = 文章訊息，包含作者ID、標題、文章人氣、時間和內文
    article = getArticleInfo(html)
    # replies = 所有回覆並包在 article裡
    replies = getAllArticleReplies(html, indexUrl + briefArticle["href"])
    article["replies"] = replies
    # 回傳詳細文章 article
    return article


# 獲得文章訊息(作者ID、標題、文章人氣、時間和內文)
def getArticleInfo(html):
    root = bs4.BeautifulSoup(html, "lxml")
    Title = root.find("meta", property="og:title")["content"]
    InfoHTML = root.find("div", class_="single-post")
    authorId = InfoHTML.find("div", class_="fn").a.string
    # 因為 popularity有可能是空白，所以要額外加判斷
    popularity = InfoHTML.find("div", class_="info").text.replace("文章人氣: ", "").replace(",", "")
    if popularity == " ":
        popularity = 0
    else:
        popularity = int(popularity)
    postTime = InfoHTML.find("div", class_="date").text.split("#")[0].replace(u'\xa0', u'')
    content = InfoHTML.find("div", class_="single-post-content").text
    # 把文章資訊包成 dictionary 並回傳
    return {"authorid": authorId, "title": Title, "popularity": popularity, "posttime": postTime, "content": content}


# 獲得文章內的所有回覆
def getAllArticleReplies(indexHTML, indexUrl):
    # 先拿到此篇文章的最大頁數
    maxPage = getMaxPage(indexHTML)
    AllArticleReplies = []
    # 依序搜尋每篇頁數內的文章
    for page in range(1, maxPage + 1):
        url = indexUrl + "&p=" + str(page)
        # 獲得單頁內的回覆，並加到 AllArticleReplies
        onePageReplies = getOnePageReplies(url)
        AllArticleReplies.extend(onePageReplies)
    return AllArticleReplies


# 獲得此篇文章的最大頁數
def getMaxPage(indexHTML):
    root = bs4.BeautifulSoup(indexHTML, "lxml")
    # 獲得 var maxpage 的數字
    pattern = re.compile(r'maxpage = (\d+)')
    scripts = root.find_all("script", text=pattern)
    maxpage = 1
    for script in scripts:
        maxpage = int(pattern.search(script.text).group(1))
    return maxpage


# 獲得單頁內的所有回覆
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
            # 回覆的內容內有些會引用樓主的話，這邊是想刪除引用
            # 因為引用的話會包在 <blockquote> 裡，
            # 所以這邊 會檢查是否有 <blockquote>，有就刪除
            blockquote = contentHTML.find("blockquote")
            if blockquote:
                contentHTML.blockquote.decompose()
            content = contentHTML.text
            # 把回覆資訊包成 dictionary 並加到 onePageReplies
            onePageReplies.append({"authorid": authorId, "posttime": postTime, "content": content})
    # 回傳單頁內的所有回覆 onePageReplies
    return onePageReplies


# 把資料輸出成 JSON 檔
def JsonWiter(message):
    # 打開 articles.json，
    # 'w' 表示寫入模式，其他還有像是 'r'代表讀取、'r+'可讀可寫等等
    # 編碼模式等於 utf-8
    with open('articles.json', 'w', encoding='utf-8') as outfile:
        # ensure_ascii = False 不要轉成 ASCII
        # indent = 4 縮排 = 4，方便閱讀
        json.dump(message, outfile, ensure_ascii = False, indent = 4)