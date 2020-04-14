import re
import time
from collections import Counter

from sqlalchemy import func

from data_spider.create_tables import Session, JobData, SearchInfo

import jieba.analyse

import jieba

jieba.add_word('五险一金')
jieba.add_word('六险一金')
jieba.add_word('带薪年假')
jieba.add_word('带薪病假')
jieba.add_word('周末双休')
jieba.add_word('年底双薪')


class HandleJobData(object):
    def __init__(self):
        self.mysql_session = Session()
        self.date = time.strftime("%Y-%m-%d", time.localtime())

    def insert_job_data(self, item, key_word):
        data = JobData(
            # 岗位ID
            position_id=item['positionId'],
            # 经度
            longitude=item['longitude'],
            # 纬度
            latitude=item['latitude'],
            # 岗位名称
            position_name=item['positionName'],
            # 工作年限
            work_year=item['workYear'],
            # 学历
            education=item['education'],
            # 岗位性质
            job_nature=item['jobNature'],
            # 公司类型
            finance_stage=item['financeStage'],
            # 公司规模
            company_size=item['companySize'],
            # 业务方向
            industry_field=item['industryField'],
            # 所在城市
            city=item['city'],
            # 岗位标签
            position_advantage=item['positionAdvantage'],
            # 公司简称
            company_short_name=item['companyShortName'],
            # 公司全称
            company_full_name=item['companyFullName'],
            # 公司所在区
            district=item['district'],
            # 公司福利标签
            company_label_list=','.join(item['companyLabelList']),
            # 工资
            salary=item['salary'],
            # 岗位发布日期
            publish_date=item['createTime'][0:10],
            # 抓取日期
            crawl_date=self.date,
            # 爬取的关键字
            key_word=key_word
        )
        query_result = self.mysql_session.query(JobData).filter(
            JobData.position_id == item['positionId'], JobData.key_word == key_word).first()
        if query_result:
            print('该岗位信息已存在%s:%s:%s' % (
                item['positionId'], item['city'], item['positionName']))
        else:
            self.mysql_session.add(data)
            self.mysql_session.commit()
            print('新增岗位信息%s' % item['positionId'])

    # 获取行业信息
    def get_industryfield(self, key_word):
        info = {}
        result = self.mysql_session.query(JobData.industry_field).filter(JobData.key_word == key_word).all()
        result_list1 = []
        for x in result:
            if x:
                res = x[0].split(',')[0]
                result_list1.append(res)

        result_list2 = [x for x in Counter(result_list1).items()]
        data = [{'name': x[0], 'value': x[1]} for x in result_list2]
        data.sort(key=lambda item: (item.get('value', 0)), reverse=True)
        if len(data) > 6:
            data = data[0:6]
        name_list = [d['name'] for d in data]
        info['x_name'] = name_list
        info['data'] = data
        return info

    # 获取薪资情况，计算方式待优化
    def get_salary(self, key_word):
        info = {}
        data = [
            {
                'name': '5k-10k',
                'value': 0
            },
            {
                'name': '10k-15k',
                'value': 0
            },
            {
                'name': '15k-20k',
                'value': 0
            },
            {
                'name': '20k-25k',
                'value': 0
            },
            {
                'name': '25k-35k',
                'value': 0
            },
            {
                'name': '35k-40k',
                'value': 0
            },
            {
                'name': '45k以上',
                'value': 0
            }
        ]
        result = self.mysql_session.query(JobData.salary).filter(JobData.key_word == key_word).all()
        result_list1 = [x[0].split(',')[0] for x in result]
        for r in result_list1:
            money = r.split('-')
            if len(money) == 1:
                data[0]['value'] += 1
                continue
            x, y = (int)(money[0][0:-1]), (int)(money[1][0:-1])
            avg = (x + y) / 2

            if avg < 10:
                data[0]['value'] += 1
            elif avg >= 10 and avg < 15:
                data[1]['value'] += 1
            elif avg >= 15 and avg < 20:
                data[2]['value'] += 1
            elif avg >= 20 and avg < 25:
                data[3]['value'] += 1
            elif avg >= 25 and avg < 35:
                data[4]['value'] += 1
            elif avg >= 35 and avg < 45:
                data[5]['value'] += 1
            else:
                data[6]['value'] += 1
        data.sort(key=lambda item: item.get('value'), reverse=True)
        name_list = [d['name'] for d in data]
        info['x_name'] = name_list
        info['data'] = data
        return info

    # 获取工作年限情况
    def get_worker_year(self, key_word):
        info = {}
        result = self.mysql_session.query(JobData.work_year).filter(JobData.key_word == key_word).all()
        result_list1 = [x[0].split(',')[0] for x in result]
        result_list2 = [x for x in Counter(result_list1).items()]
        data = [{'name': x[0], 'value': x[1]} for x in result_list2]
        data.sort(key=lambda item: item.get('value'), reverse=True)
        name_list = [d['name'] for d in data]
        info['x_name'] = name_list
        info['data'] = data
        return info

    # 获取学历情况
    def get_education(self, key_word):
        info = {}
        result = self.mysql_session.query(JobData.education).filter(JobData.key_word == key_word).all()
        result_list1 = [x[0].split(',')[0] for x in result]
        result_list2 = [x for x in Counter(result_list1).items()]
        data = [{'name': x[0], 'value': x[1]} for x in result_list2]
        name_list = [d['name'] for d in data]
        info['x_name'] = name_list
        info['data'] = data
        return info

    # 按照日期计算岗位发布数量
    def get_job_number_by_date(self, key_word):
        info = {}
        result = self.mysql_session.query(JobData.publish_date, func.count(
            '*').label('c')).filter(JobData.key_word == key_word).group_by(
            JobData.publish_date).all()
        # result1 = [{'name': x[0][5:10], 'value': x[1]} for x in result]
        data = [
            {
                'name': '春季',
                'value': 0
            },
            {
                'name': '夏季',
                'value': 0
            },
            {
                'name': '秋季',
                'value': 0
            },
            {
                'name': '冬季',
                'value': 0
            }
        ]
        for x in result:
            index, month = 3, int(x[0][5:7])
            if month >= 3 and month <= 5:
                index = 0
            elif month >= 6 and month <= 8:
                index = 1
            elif month >= 9 and month <= 11:
                index = 2
            data[index]['value'] += x[1]
        name_list = [res['name'] for res in data]
        info['x_name'] = name_list
        info['data'] = data
        return info

    # 根据城市计算岗位数量
    def get_job_number_by_city(self, key_word):
        info = {}
        result = self.mysql_session.query(JobData.city, func.count(
            '*').label('c')).filter(JobData.key_word == key_word).group_by(
            JobData.city).all()
        result1 = [{'name': x[0], 'value': x[1]} for x in result]
        name_list = [res['name'] for res in result1]
        info['x_name'] = name_list
        info['data'] = result1
        print(info)
        return info

    # 获取融资情况
    def get_fiance_stage(self, key_word):
        info = {}
        result = self.mysql_session.query(JobData.finance_stage, func.count(
            '*').label('c')).filter(JobData.key_word == key_word).group_by(
            JobData.finance_stage).all()
        result1 = [{'name': x[0], 'value': x[1]} for x in result]
        name_list = [res['name'] for res in result1]
        info['x_name'] = name_list
        info['data'] = result1
        return info

    # 获取公司规模
    def get_company_size(self, key_word):
        info = {}
        result = self.mysql_session.query(JobData.company_size, func.count(
            '*').label('c')).filter(JobData.key_word == key_word).group_by(
            JobData.company_size).all()
        result1 = [{'name': x[0], 'value': x[1]} for x in result]
        name_list = [res['name'] for res in result1]
        info['x_name'] = name_list
        info['data'] = result1
        return info

    # 获取岗位要求
    def get_job_nature(self, key_word):
        info = {}
        result = self.mysql_session.query(JobData.job_nature, func.count(
            '*').label('c')).filter(JobData.key_word == key_word).group_by(
            JobData.job_nature).all()
        result1 = [{'name': x[0], 'value': x[1]} for x in result]
        name_list = [res['name'] for res in result1]
        info['x_name'] = name_list
        info['data'] = result1
        return info

    # 获取抓取数量
    def get_crawl_number(self, key_word):
        info = {}
        info['today_count'] = self.mysql_session.query(JobData).filter(
            JobData.crawl_date == self.date,
            JobData.key_word == key_word).count()
        info['all_count'] = self.mysql_session.query(JobData).filter(
            JobData.key_word == key_word).count()
        return info

    # 首页热门搜索
    def query_hot_search(self):
        result = self.mysql_session.query(JobData.key_word, func.count("*").label("count")).group_by(
            JobData.key_word).all()
        # data = [{"name": d[0], "value": d[1]} for d in result]
        data = [{"name": d.key_word, "value": d.count} for d in result]
        return data

    # 查询关键字被搜索情况
    def query_search_info(self, key_word=None):
        self.mysql_session.commit()
        if not key_word:
            return self.mysql_session.query(SearchInfo).filter(
                SearchInfo.search_time > 3).all()

        return self.mysql_session.query(SearchInfo).filter(
            SearchInfo.job_name == key_word).first()

    # 更新关键字搜索
    def update_search_info(self, key_word):
        query_result = self.query_search_info(key_word)

        if query_result:
            # 更新关键词的搜索次数
            query_result.search_time = query_result.search_time + 1
        else:
            # 新增一条记录
            data = SearchInfo(
                job_name=key_word,
                search_time=1
            )
            self.mysql_session.add(data)
        self.mysql_session.commit()

    # 分词
    def split_word(self, src):
        result_str = ""
        for x in src:
            result_str += str.strip(str(x))
        # 使用正则表达式去除标点符号
        r = '[’!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]+'
        new_result_str = re.sub(r, '', result_str)
        # # 使用结巴分词
        # jieba.analyse.set_stop_words("baidu_stopwords.txt")
        # jieba.analyse.set_idf_path("idf.txt")
        result_list1 = jieba.analyse.extract_tags(result_str, 50, True)
        # result_list1 = jieba.cut(new_result_str, cut_all=False)
        result_list2 = [{'name': item[0], 'value': int(item[1] * len(result_str))} for item in result_list1]
        return result_list2

    # 获取福利标签
    def get_company_label(self, key_word):
        info = {}
        result = self.mysql_session.query(JobData.company_label_list).filter(JobData.key_word == key_word)
        res = self.split_word(result)
        info['data'] = res
        return info

    # 获取岗位优势
    def get_position_advantage(self, key_word):
        info = {}
        result = self.mysql_session.query(JobData.position_advantage).filter(JobData.key_word == key_word)
        res = self.split_word(result)
        # data = [{'name': x[0], 'value': x[1]} for x in res]
        info['data'] = res
        return info

    def get_position_num_and_avg_salary_by_city(self, key_word):
        info = []
        num = func.count("*").label("num")
        for edu in ['大专', '本科', '硕士']:
            result = self.mysql_session.query(func.avg(JobData.salary) * 1000, num, JobData.city,
                                              JobData.education).filter(JobData.key_word == key_word,
                                                                        JobData.education == edu).group_by(
                JobData.city).order_by(num.desc()).limit(10).all()
            info.append(result)
        return info


dao = HandleJobData()
