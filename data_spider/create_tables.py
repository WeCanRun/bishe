from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 创建数据库的连接
engine = create_engine("mysql+mysqlconnector://root:root@127.0.0.1:3306/bishe"
                       "?charset=utf8mb4&auth_plugin=mysql_native_password")

# 连接数据库的 session
Session = sessionmaker(bind=engine)
# 创建对象的基类:
Base = declarative_base()


class JobData(Base):
    # 表名
    __tablename__ = 'job_data'
    # 表结构
    # id,设置为主键和自动增长
    id = Column(Integer, primary_key=True, autoincrement=True)
    # 岗位ID,非空字段
    position_id = Column(Integer, nullable=False)
    # 爬取的关键字
    key_word = Column(String(length=20), nullable=False)
    # 经度
    longitude = Column(Float, nullable=True)
    # 纬度
    latitude = Column(Float, nullable=True)
    # 岗位名称
    position_name = Column(String(length=50), nullable=False)
    # 工作年限
    work_year = Column(String(length=20), nullable=False)
    # 学历
    education = Column(String(length=20), nullable=False)
    # 岗位性质
    job_nature = Column(String(length=20), nullable=True)
    # 公司类型
    finance_stage = Column(String(length=30), nullable=True)
    # 公司规模
    company_size = Column(String(length=30), nullable=True)
    # 业务方向
    industry_field = Column(String(length=30), nullable=True)
    # 所在城市
    city = Column(String(length=10), nullable=False)
    # 岗位标签
    position_advantage = Column(String(length=200), nullable=True)
    # 公司简称
    company_short_name = Column(String(length=50), nullable=True)
    # 公司全称
    company_full_name = Column(String(length=200), nullable=True)
    # 公司所在区
    district = Column(String(length=20), nullable=True)
    # 公司福利标签
    company_label_list = Column(String(length=200), nullable=True)
    # 工资
    salary = Column(String(length=20), nullable=False)
    # 发布日期
    publish_date = Column(String(length=20), nullable=False)
    # 抓取日期
    crawl_date = Column(String(length=20), nullable=False)


class SearchInfo(Base):
    __tablename__ = 'search_info'

    # 表结构
    # id,设置为主键和自动增长
    id = Column(Integer, primary_key=True, autoincrement=True)
    # 岗位名字
    job_name = Column(String(length=20), nullable=False)
    # 搜索次数
    search_time = Column(Integer, nullable=False)


if __name__ == '__main__':
    JobData.metadata.create_all(engine)
    SearchInfo.metadata.create_all(engine)
