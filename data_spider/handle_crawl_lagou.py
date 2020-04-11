import os
import sys

import requests
import datetime
import time
import json
import re
import sched
import time
from multiprocessing.pool import Pool
sys.path.append(os.path.abspath(".."))

from data_spider.insert_data import dao


class HandleLagou(object):
    def __init__(self):
        self.lagou_session = requests.session()
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) +'
                          'Chrome/73.0.3683.86 Safari/537.36'
        }
        self.city_list = ""
        self.keywords = ""

    def handle_request(self, method, url, data=None, info=None):
        while True:
            proxyinfo = "http://%s:%s@%s:%s" % ('HQ38D6P49P27839C',
                                                'ACFFAA8D21244264',
                                                'http-cla.abuyun.com', '9030')
            proxy = {
                "http": proxyinfo,
                "https": proxyinfo
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
                self.handle_request_exception(city=info)
                continue

            response.encoding = 'utf-8'
            if '频繁' in response.text:
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
        self.handle_request(method="GET", url=first_request_url)
        time.sleep(10)

    def get_citys(self):
        # <a href=" https://www.lagou.com/langfang-zhaopin/">廊坊</a>
        city_search = re.compile(r'www.lagou.com/.*/">(.*?)</a>')
        city_url = "https://www.lagou.com/jobs/allCity.html"
        city_res = self.handle_request(method="GET", url=city_url)
        # 使用正则匹配城市信息
        self.city_list = set(city_search.findall(city_res))
        self.lagou_session.cookies.clear()

    def get_keywords(self):
        keywords_search = re.compile(r'https://www.lagou.com/zhaopin.*<h3>(.*?)</h3></a>')
        keywords_url = "https://www.lagou.com/"
        keywords_res = self.handle_request(method="GET", url=keywords_url)
        self.keywords = set(keywords_search.findall(keywords_res))
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
    print(lagou.city_list)
    lagou.get_keywords()
    print(lagou.keywords)
    # for city in lagou.city_list:
    #     for kd in lagou.keywords:
    #         lagou.get_city_job(city, kd)
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
