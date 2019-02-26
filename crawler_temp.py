import urllib.request as request

# 抓取 mobile01 網頁原始碼
url = "https://www.mobile01.com/topiclist.php?f=383"

with request.urlopen(url) as response:
    data = response.read().decode("utf-8")

# 解析原始碼
import bs4
root = bs4.BeautifulSoup(data, "html.parser")
titles = root.find_all("td", class_="authur") # 尋找 class="subject-text" span 標籤
count = 1
for title in titles:
    print(count, title)
    count+=1