#coding=utf-8

import time
from bs4 import BeautifulSoup
from pymongo import MongoClient
import requests
import urlparse
import json
import redis
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def search_all_page_url():
    start_url = 'https://www.taptap.com/top/cn'
    r = requests.get(start_url)
    detailList = []
    if r.status_code == 200:
        time.sleep(2)
        bs = BeautifulSoup(r.text, 'html5lib')
        # print "conet:", bs
        urlList = bs.select("#topList .taptap-top-card")
        # print urlList[0]
        for i in urlList:
            detailList.append(i.select(".card-left-image")[0].get("href"))
        # if "none" in bs.select(".taptap-button-more button")[0].get("style"):
        # print "adwadwa:", bs.select(".col-sm-12 .taptap-button-more")
        if bs.select(".col-sm-12 .taptap-button-more button"):
            url2 = bs.select(".col-sm-12 .taptap-button-more button")[0].get("data-url")
            # more_content(url2)
            detailList.extend(more_content(url2))
    else:
        print "页面信息获取失败"
    return detailList

def devide_url():
    urls = search_all_page_url()
    for i in urls:
        search_content(i)

def search_content(url):
    print "awdada:", url
    r = requests.get(url)
    if r.status_code == 200:
        # time.sleep(2)
        bs = BeautifulSoup(r.text, 'html5lib')
        gameObj = {}
        gameObj["game_id"] = bs.select(".taptap-button-download")[0].get("data-app-id") #游戏id
        gameObj["name"] = bs.select(".header-icon-body img")[0].get("title")    #游戏名称
        gameObj["iconSrc"] = bs.select(".header-icon-body img")[0].get("src")   #游戏图标
        gameObj["timesdownload"] = bs.select(".text-download-times")[0].text.replace("次安装", "")    #游戏下载次数
        gameObj["score"] = bs.select(".app-rating-score")[0].text   #游戏评分
        gameObj["review"] = bs.select(".main-header-tab ul li")[1].select("a small")[0].text    #游戏评价数
        for i in bs.select(".info-item-content"):
            if(i.get("itemprop") ==  "datePublished"):
                gameObj["refresh_time"] = i.text    #游戏更新时间
        single_data_save_mysql(gameObj)
        print "游戏相关信息如下：", gameObj

def more_content(url2):
    print "awdad:", url2
    urls = []
    r = requests.get(url2)
    if r.status_code == 200:
        # time.sleep(2)
        msgData = json.JSONDecoder().decode(r.text)
        print msgData
        if(msgData["data"]["next"]):
            more_content(msgData["data"]["next"])
        if(msgData["data"]["html"]):
            bs = BeautifulSoup(msgData["data"]["html"], 'html5lib')
            urlList = bs.select(".taptap-top-card")
            for i in urlList:
                urls.append(i.select(".card-left-image")[0].get("href"))
    return urls


def single_data_save_mysql(dataObj):
    #建立MongoDB数据库连接
    client = MongoClient('127.0.0.1', 27017)
    #连接所需数据库,test为数据库名
    db = client.admin
    db.taplist.insert(dataObj)

if __name__ == '__main__':
    print "爬虫开始工作..."
    devide_url()
    print "爬取工作结束..."
