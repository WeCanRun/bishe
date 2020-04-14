import os
import sys

import requests
import datetime
import time
import json
import re
import sched
import time

sys.path.append(os.path.abspath(".."))

from multiprocessing.pool import Pool

from data_spider.setting import *

from data_spider.insert_data import dao

from pyquery import PyQuery as py

bad_ip_pool = set()
all_ip = set()


class HandleLagou(object):
    def __init__(self):
        self.lagou_session = requests.session()
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) +'
                          'Chrome/73.0.3683.86 Safari/537.36'
        }
        self.proxyinfo = PROXY_INFO
        self.city_list = ""
        self.keywords = ""

    def get_random_proxy(self):
        """
        get random proxy from proxypool
        :return: proxy
        """
        return requests.get(PROXY_POOL_URL).text.strip()

    def handle_request(self, method, url, data=None, info=None):
        while True:
            # proxy_ip = self.get_random_proxy()
            # print("get random proxy ip ", proxy_ip)

            # proxy_ip = requests.get(ZHIMA_URL).text.strip()
            # all_ip.add(proxy_ip)
            # proxy = {
            #     'http': 'http://' + proxy_ip,
            #     'https': 'https://' + proxy_ip
            # }
            proxy = {
                "http": self.proxyinfo,
                "https": self.proxyinfo,
            }
            try:
                if method == "GET":
                    response = self.lagou_session.get(url=url,
                                                      headers=self.header,
                                                      proxies=proxy, timeout=6)
                elif method == "POST":
                    response = self.lagou_session.post(url=url,
                                                       headers=self.header,
                                                       data=data, proxies=proxy,
                                                       timeout=6)
            except:
                # bad_ip_pool.add(proxy_ip)
                # print(bad_ip_pool)
                # print("bad_ip_poil: {}, all_ip:{}".format(len(bad_ip_pool), len(all_ip)))
                self.handle_request_exception(city=info)
                continue

            response.encoding = 'utf-8'
            if '频繁' in response.text:
                # bad_ip_pool.add(proxy_ip)
                # print(bad_ip_pool)
                # print("bad_ip_pool: {}, all_ip:{}".format(len(bad_ip_pool), len(all_ip)))
                print(response.text)
                self.handle_request_exception(city=info)
                continue

            return response.text

    def handle_request_exception(self, city):
        print('handle exception')
        # 清理 cookies 信息
        self.lagou_session.cookies.clear()
        # 重新获取 cookies 信息
        first_request_url = "https://www.lagou.com/jobs/list_python?city=%s&cl=false&fromSearch=true+ " \
                            "&labelWords=&suginput=" % city
        time.sleep(5)
        self.handle_request(method="GET", url=first_request_url)
        time.sleep(5)

    def get_citys(self):
        # <a href=" https://www.lagou.com/langfang-zhaopin/">廊坊</a>
        city_search = re.compile(r'www.lagou.com/.*/">(.*?)</a>')
        city_url = "https://www.lagou.com/jobs/allCity.html"
        city_res = self.handle_request(method="GET", url=city_url)
        # 使用正则匹配城市信息
        self.city_list = set(city_search.findall(city_res))
        self.lagou_session.cookies.clear()

    def get_keywords(self):
        # keywords_search = re.compile(r'https://www.lagou.com/zhaopin.*<h3>(.*?)</h3></a>', re.S)
        keywords_url = "https://www.lagou.com/"
        keywords_res = self.handle_request(method="GET", url=keywords_url)
        doc = py(keywords_res)
        res = doc("#sidebar > div > div:nth-child(1) a h3")
        # self.keywords = set(keywords_search.findall(keywords_res))
        self.keywords = set(res.text().split(" "))
        self.lagou_session.cookies.clear()

    def get_city_job(self, city, key_word):
        first_request_url = "https://www.lagou.com/jobs/list_python?city=%s&cl=false&fromSearch=true& + " \
                            "labelWords=&suginput=" % city
        first_response = self.handle_request(method="GET",
                                             url=first_request_url)
        total_page_search = re.compile(r'class="span\stotalNum">(\d+)</span>')
        try:
            total_page = total_page_search.search(first_response).group(1)
            print(city, total_page)
        except:
            return
        else:
            for i in range(1, int(total_page) + 1):
                data = {
                    "pn": i,
                    "kd": key_word
                }
                page_url = "https://www.lagou.com/jobs/positionAjax.json?city=%s&needAddtionalResult=false" % city
                referer_url = "https://www.lagou.com/jobs/list_python?city=%s&cl=false&fromSearch=true+" \
                              "&labelWords=&suginput=" % city
                # referer的URL需要进行encode
                self.header['Referer'] = referer_url.encode()
                response = self.handle_request(method="POST", url=page_url,
                                               data=data)
                lagou_data = json.loads(response)
                job_list = lagou_data['content']['positionResult']['result']
                print("job_list %d" % i)
                for job in job_list:
                    dao.insert_job_data(job, key_word=key_word)


# 运行爬虫
def run_spider():
    lagou = HandleLagou()
    lagou.get_citys()
    print(type(lagou.city_list), lagou.city_list)
    lagou.get_keywords()
    print(type(lagou.keywords), lagou.keywords)
    lagou.keywords = ['Java', 'Python', 'Go', '前端', '后端', 'JavaScript', '测试', '服务端', 'PHP', '软件开发工程师',
                      '大数据开发']
    pool = Pool(2)
    for city in lagou.city_list:
        for kd in lagou.keywords:
            # pool.map(lagou.get_city_job, city, kd)
            pool.apply_async(lagou.get_city_job, args=(city, kd,))
    pool.close()
    pool.join()


# 定时任务
def scheduled_task(hour=1, minute=0):
    # 暴力方法一：
    # while True:
    #     now = datetime.datetime.now()
    #     if now.hour == hour and now.minute == minute:
    #         run_spider()
    #         print("爬虫耗时：", datetime.datetime.now() - now)
    #     time.sleep(59)

    # 优雅方法二：
    # scheduler = sched.scheduler(time.time, time.sleep)
    # # 增加调度任务
    # runtime = datetime.datetime(2020, 4, 10, 16, 36, 30)
    # time_stamp = time.mktime(runtime.timetuple())
    # scheduler.enterabs(time_stamp, 1, run_spider())
    # # 运行任务
    # scheduler.run()
    # print(runtime, time_stamp)
    pass


if __name__ == '__main__':
    print("=" * 20, "start", "=" * 20)
    run_spider()
    print("=" * 20, "finish", "=" * 20)
