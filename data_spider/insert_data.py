import time
from collections import Counter

from sqlalchemy import func

from data_spider.create_tables import Session, JobData, SearchInfo


class HandleJobData(object):
    def __init__(self):
        self.mysql_session = Session()
        # self.date = time.strftime("%Y-%m-%d", time.localtime())
        self.date = '2020-02-12'

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
            JobData.crawl_date == self.date,
            JobData.position_id == item['positionId']).first()
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
        result = self.mysql_session.query(JobData.industry_field).filter(
            JobData.crawl_date == self.date, JobData.key_word == key_word).all()
        result_list1 = []
        for x in result:
            res = x[0].split(',')[0]
            if res == '移动互联网':
                res = res[2:5]
            result_list1.append(res)
        # result_list1 = [x[0].split(',')[0] for x in result]
        result_list2 = [x for x in Counter(result_list1).items()]
        data = [{'name': x[0], 'value': x[1]} for x in result_list2 if x[1] >
                30]
        name_list = [d['name'] for d in data]
        info['x_name'] = name_list
        info['data'] = data
        print(info)
        return info

    # 获取薪资情况
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
        result = self.mysql_session.query(JobData.salary).filter(
            JobData.crawl_date == self.date, JobData.key_word == key_word).all()
        result_list1 = [x[0].split(',')[0] for x in result]
        # result_list2 = [x for x in Counter(result_list1).items()]
        # data = [{'name': x[0], 'value': x[1]} for x in result_list2 if x[1] >
        #         50]
        # name_list = [d['name'] for d in data]
        # info['x_name'] = name_list
        # info['data'] = data
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

        name_list = [d['name'] for d in data]
        info['x_name'] = name_list
        info['data'] = data
        print(info)
        return info

    # 获取工作年限情况
    def get_worker_year(self, key_word):
        info = {}
        result = self.mysql_session.query(JobData.work_year).filter(
            JobData.crawl_date == self.date, JobData.key_word == key_word).all()
        result_list1 = [x[0].split(',')[0] for x in result]
        result_list2 = [x for x in Counter(result_list1).items()]
        data = [{'name': x[0], 'value': x[1]} for x in result_list2]
        name_list = [d['name'] for d in data]
        info['x_name'] = name_list
        info['data'] = data
        print(info)
        return info

    # 获取学历情况
    def get_education(self, key_word):
        info = {}
        result = self.mysql_session.query(JobData.education).filter(
            JobData.crawl_date == self.date, JobData.key_word == key_word).all()
        result_list1 = [x[0].split(',')[0] for x in result]
        result_list2 = [x for x in Counter(result_list1).items()]
        data = [{'name': x[0], 'value': x[1]} for x in result_list2]
        name_list = [d['name'] for d in data]
        info['x_name'] = name_list
        info['data'] = data
        print(info)
        return info

    # 按照日期计算岗位发布数量
    def get_job_number_by_date(self, key_word):
        info = {}
        result = self.mysql_session.query(JobData.publish_date, func.count(
            '*').label('c')).filter(JobData.key_word == key_word).group_by(
            JobData.publish_date).order_by(
            JobData.publish_date).all()
        result1 = [{'name': x[0][5:10], 'value': x[1]} for x in result if x[
            1] >= 8]
        name_list = [res['name'] for res in result1]
        info['x_name'] = name_list
        info['data'] = result1
        print(info)
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
        print(info)
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
        print(info)
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
        print(info)
        return info

    # 获取抓取数量
    def get_crawl_number(self, key_word):
        info = {}
        info['today_count'] = self.mysql_session.query(JobData).filter(
            JobData.crawl_date == self.date,
            JobData.key_word == key_word).count()
        info['all_count'] = self.mysql_session.query(JobData).filter(
            JobData.key_word == key_word).count()
        print(info)
        return info

    def query_search_info(self, key_word=None):
        self.mysql_session.commit()
        if not key_word:
            return self.mysql_session.query(SearchInfo).filter(
                SearchInfo.search_time > 3).all()

        return self.mysql_session.query(SearchInfo).filter(
            SearchInfo.job_name == key_word).first()

    def update_search_info(self, key_word):
        query_result = self.query_search_info(key_word)

        if query_result:
            query_result.search_time = query_result.search_time + 1
        else:
            data = SearchInfo(
                job_name=key_word,
                search_time=1
            )
            self.mysql_session.add(data)
        self.mysql_session.commit()


dao = HandleJobData()
