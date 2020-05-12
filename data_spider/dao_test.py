import time

from data_spider.insert_data import dao, get_pest_data

key_word_test = ['java', 'python', 'golang']

item = {
    # 岗位ID
    "positionId": 2,
    # 经度
    'longitude': 11,
    # 纬度
    'latitude': 22,
    # 岗位名称
    'positionName': 'positionName',
    # 工作年限
    'workYear': '3-5',
    # 学历
    'education': 'education',
    # 岗位性质
    'jobNature': 'jobNature',
    # 公司类型
    'financeStage': 'financeStage',
    # 公司规模
    'companySize': 'companySize',
    # 业务方向
    'industryField': 'industryField',
    # 所在城市
    'city': 'city',
    # 岗位标签
    'positionAdvantage': 'positionAdvantage',
    # 公司简称
    'companyShortName': 'companyShortName',
    # 公司全称
    'companyFullName': 'companyFullName',
    # 公司所在区
    'district': 'district',
    # 公司福利标签
    'companyLabelList': 'companyLabelList',
    # 工资
    'salary': '222',
    # 岗位发布日期
    'createTime': '2020-02-12',
}

if __name__ == '__main__':
    for kd in key_word_test:
        print("kd =", kd)
        # dao.insert_job_data(item, key_word=kd)
        # dao.get_industryfield(kd)
        # dao.get_salary(kd)
        dao.get_worker_year(kd)
        # dao.get_education(kd)
        # dao.get_job_number_by_date(kd)
        # dao.get_job_number_by_city(kd)
        # dao.get_fiance_stage(kd)
        # dao.get_company_size(kd)
        # dao.get_job_nature(kd)
        # dao.get_crawl_number(kd)
        # dao.update_search_info(kd)
        # dao.get_company_label(kd)
        # dao.get_position_advantage(kd)
        # dao.get_position_num_and_avg_salary_by_city(kd)
    # dao.query_hot_search()
    # get_pest_data()