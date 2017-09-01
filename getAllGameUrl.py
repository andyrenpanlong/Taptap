#coding=utf-8

import time
from bs4 import BeautifulSoup
from pymongo import MongoClient
import requests
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
detailList = []
billboard = {
    "hot": {
        "name": "热门游戏榜",
        "classify": [""]
    },
    "cn": "中国榜",
    "us": "美国榜",
    "jp": "日本榜",
    "tw": "台湾榜",
    "hk": "香港榜",
}

def search_all_page_url():
    start_url = 'https://www.taptap.com/top/download'
    r = requests.get(start_url)
    if r.status_code == 200:
        # time.sleep(2)
        bs = BeautifulSoup(r.text, 'html5lib')
        urlList = bs.select("#page-top .taptap-tab-nav li")
        for i in urlList:
            if "developer" not in i.get("class"):
                get_tab_url(i.select("a")[0].get("href"))

def get_tab_url(url):
    r = requests.get(url)
    if r.status_code == 200:
        # time.sleep(2)
        bs = BeautifulSoup(r.text, 'html5lib')
        urlList = bs.select(".app-top-switch li")
        for i in urlList:
            dataObj = {}
            dataObj["url"] = i.select("a")[0].get("href")
            dataObj["name"] = i.select("a")[0].text
            single_data_save_mysql(dataObj)

def single_data_save_mysql(dataObj):
    #建立MongoDB数据库连接
    client = MongoClient('127.0.0.1', 27017)
    #连接所需数据库,test为数据库名
    db = client.admin
    db.gameAllList.insert(dataObj)

if __name__ == '__main__':
    print "爬虫开始工作..."
    search_all_page_url()
    for i in detailList:
        print i
    print "爬取工作结束..."
