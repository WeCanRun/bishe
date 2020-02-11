import time
from collections import Counter

from sqlalchemy import func

from data_spider.create_tables import Session, JobInfo


class HandleJobInfo(object):
    def __init__(self):
        self.mysql_session = Session()
        self.date = time.strftime("%Y-%m-%d", time.localtime())
        # self.date = '2020-02-07'

    def insert_job_info(self, item):
        data = JobInfo(
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
            salary=item['salary'],
            publish_date=item['createTime'][0:10],
            # 抓取日期
            crawl_date=self.date
        )
        query_result = self.mysql_session.query(JobInfo).filter(
            JobInfo.crawl_date == self.date,
            JobInfo.position_id == item['positionId']).first()
        if query_result:
            print('该岗位信息已存在%s:%s:%s' % (
                item['positionId'], item['city'], item['positionName']))
        else:
            self.mysql_session.add(data)
            self.mysql_session.commit()
            print('新增岗位信息%s' % item['positionId'])

    # 获取行业信息
    def get_industryfield(self):
        info = {}
        result = self.mysql_session.query(JobInfo.industry_field).filter(
            JobInfo.crawl_date == self.date).all()
        result_list1 = [x[0].split(',')[0] for x in result]
        result_list2 = [x for x in Counter(result_list1).items() if x[1] > 50]
        data = [{'name': x[0], 'value': x[1]} for x in result_list2]
        name_list = [d['name'] for d in data]
        info['x_name'] = name_list
        info['data'] = data
        print(info)
        return info

    # 获取薪资情况
    def get_salary(self):
        info = {}
        result = self.mysql_session.query(JobInfo.salary).filter(
            JobInfo.crawl_date == self.date).all()
        result_list1 = [x[0].split(',')[0] for x in result]
        result_list2 = [x for x in Counter(result_list1).items() if x[1] > 50]
        data = [{'name': x[0], 'value': x[1]} for x in result_list2]
        name_list = [d['name'] for d in data]
        info['x_name'] = name_list
        info['data'] = data
        print(info)
        return info

    # 获取工作年限情况
    def get_worker_year(self):
        info = {}
        result = self.mysql_session.query(JobInfo.work_year).filter(
            JobInfo.crawl_date == self.date).all()
        result_list1 = [x[0].split(',')[0] for x in result]
        result_list2 = [x for x in Counter(result_list1).items() if x[1] > 50]
        data = [{'name': x[0], 'value': x[1]} for x in result_list2]
        name_list = [d['name'] for d in data]
        info['x_name'] = name_list
        info['data'] = data
        print(info)
        return info

    # 获取学历情况
    def get_education(self):
        info = {}
        result = self.mysql_session.query(JobInfo.education).filter(
            JobInfo.crawl_date == self.date).all()
        result_list1 = [x[0].split(',')[0] for x in result]
        result_list2 = [x for x in Counter(result_list1).items()]
        data = [{'name': x[0], 'value': x[1]} for x in result_list2]
        name_list = [d['name'] for d in data]
        info['x_name'] = name_list
        info['data'] = data
        print(info)
        return info

    # 按照日期计算岗位发布数量
    def get_job_number_by_date(self):
        info = {}
        result = self.mysql_session.query(JobInfo.publish_date, func.count(
            '*').label('c')).group_by(JobInfo.publish_date).all()
        result1 = [{'name': x[0], 'value': x[1]} for x in result]
        name_list = [res['name'] for res in result1]
        info['x_name'] = name_list
        info['data'] = result1
        print(info)
        return info

    # 根据城市计算岗位数量
    def get_job_number_by_city(self):
        info = {}
        result = self.mysql_session.query(JobInfo.city, func.count(
            '*').label('c')).group_by(JobInfo.city).all()
        result1 = [{'name': x[0], 'value': x[1]} for x in result]
        name_list = [res['name'] for res in result1]
        info['x_name'] = name_list
        info['data'] = result1
        print(info)
        return info

    # 获取融资情况
    def get_fiance_stage(self):
        info = {}
        result = self.mysql_session.query(JobInfo.finance_stage, func.count(
            '*').label('c')).group_by(JobInfo.finance_stage).all()
        result1 = [{'name': x[0], 'value': x[1]} for x in result]
        name_list = [res['name'] for res in result1]
        info['x_name'] = name_list
        info['data'] = result1
        print(info)
        return info

    # 获取公司规模
    def get_company_size(self):
        info = {}
        result = self.mysql_session.query(JobInfo.company_size, func.count(
            '*').label('c')).group_by(JobInfo.company_size).all()
        result1 = [{'name': x[0], 'value': x[1]} for x in result]
        name_list = [res['name'] for res in result1]
        info['x_name'] = name_list
        info['data'] = result1
        print(info)
        return info

    # 获取任职要求
    def get_job_nature(self):
        info = {}
        result = self.mysql_session.query(JobInfo.job_nature, func.count(
            '*').label('c')).group_by(JobInfo.job_nature).all()
        result1 = [{'name': x[0], 'value': x[1]} for x in result]
        name_list = [res['name'] for res in result1]
        info['x_name'] = name_list
        info['data'] = result1
        print(info)
        return info

    # 获取抓取数量
    def get_crawl_number(self):
        info = {}
        info['today_count'] = self.mysql_session.query(JobInfo).filter(
            JobInfo.crawl_date == self.date).count()
        info['all_count'] = self.mysql_session.query(JobInfo).count()
        print(info)
        return info


dao = HandleJobInfo()
dao.get_salary()
dao.get_worker_year()
dao.get_education()
dao.get_job_number_by_date()
dao.get_job_number_by_city()
dao.get_fiance_stage()
dao.get_company_size()
dao.get_job_nature()
dao.get_crawl_number()
