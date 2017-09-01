#coding=utf-8
from __future__ import division
from bs4 import BeautifulSoup
from pymongo import MongoClient
import requests
import math
import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
commentUrlList = []

def search_all_page_url(start_url):
    r = requests.get(start_url)
    if r.status_code == 200:
        bs = BeautifulSoup(r.text, 'html5lib')
        if not bs.select(".main-header-tab ul li")[1].select("a small"):
            return
        all_pages = int(bs.select(".main-header-tab ul li")[1].select("a small")[0].text)    #游戏评价数
        print "review_num:", all_pages
        for page in range(1, int(math.ceil(all_pages/20)+1)):
            commentUrlList.append(start_url + "?order=default&page=" + str(page) + "#review-list")
    else:
        print "页面信息获取失败"
    # return commentUrlList

def get_all_type_url():
    #建立MongoDB数据库连接
    client = MongoClient('127.0.0.1', 27017)
    #连接所需数据库,test为数据库名
    db = client.admin
    for i in list(db.taplist.find({})):
        url = "https://www.taptap.com/app/" + str(i["game_id"]) + "/review"
        print "requests_url:", url
        search_all_page_url(url)

def devide_url():
    get_all_type_url()
    print "游戏数目：", len(detailList)
    for i in commentUrlList:
        print "游戏信息链接：", i
        search_content(i)

def search_content(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            time.sleep(1)
            bs = BeautifulSoup(r.text, 'html5lib')
            commentList = bs.select("#reviewsList .taptap-review-item")  # 评论列表
            print len(commentList)
            for i in commentList:
                gameObj = {}
                gameObj["game_id"] = bs.select(".taptap-button-download")[0].get("data-app-id")  # 游戏id
                gameObj["name"] = bs.select(".header-icon-body img")[0].get("title")  # 游戏名称
                gameObj["iconSrc"] = bs.select(".header-icon-body img")[0].get("src")  # 游戏图标
                gameObj["comment_id"] = int(i.get("id").replace("review-", ""))  # 评论id
                gameObj["user_name"] = i.select(".taptap-user-name")[0].text  # 用户名
                gameObj["user_type"] = 0  # 用户Type  type=0表示普通用户
                gameObj["user_icon"] = i.select(".review-item-avatar img")[0].get("src")  # 用户头像
                gameObj["comment_micro_time"] = i.select(".text-header-time span")[0].get(
                    "data-dynamic-time")  # 评论时间（毫秒数）
                gameObj["comment_time"] = i.select(".text-header-time span")[0].text  # 评论时间（时间戳）
                gameObj["comment_content"] = i.select(".item-text-body")[0].text or "0"  # 评论内容
                gameObj["comment_vote_num"] = i.select(".vote-up span")[0].text or "0"  # 点赞数量
                gameObj["comment_score"] = i.select(".item-text-score .colored")[0].get("style").replace("width: ",
                                                                                                         "").replace(
                    "px", "")  # 评论得分
                gameObj["comment_replay_num"] = i.select(".question-witch-replay .normal-text")[0].text.replace("回复",
                                                                                                                "").replace(
                    "(", "").replace(")", "") or str(0)  # 点赞数量
                single_data_save_mysql(gameObj)
                print "游戏相关信息如下：", gameObj
    except:  # 若出现网页读取错误捕获并输出
        print "获取正文页出错"
        pass


def single_data_save_mysql(dataObj):
    #建立MongoDB数据库连接
    client = MongoClient('127.0.0.1', 27017)
    #连接所需数据库,test为数据库名
    db = client.admin
    db.comment2.insert(dataObj)

if __name__ == '__main__':
    print "爬虫开始工作..."
    devide_url()
    print "爬取工作结束..."
