import json
import os
import sys

from flask import Flask, render_template, jsonify, request

sys.path.append(os.path.abspath(".."))

from data_spider.insert_data import dao

app = Flask(__name__)


# 首页
@app.route("/")
def index():
    return render_template("index.html")


# 按照关键字搜索
@app.route("/search/", methods=['GET'])
def search():
    key_word = request.args.get('lang')
    if key_word is None or len(key_word) > 20:
        return render_template('page_not_found.html')

    if key_word:
        dao.update_search_info(key_word)
        return render_template("show.html", key_word=key_word)
    return render_template("index.html")


# 获取填充数据
@app.route("/get_echart_data/<key_word>/", methods=['GET', 'POST'])
def get_echart_data(key_word):
    info = {}
    info['echart_1'] = dao.get_industryfield(key_word)
    info['echart_2'] = dao.get_salary(key_word)
    info['echart_4'] = dao.get_job_number_by_date(key_word)
    info['echart_5'] = dao.get_worker_year(key_word)
    info['echart_6'] = dao.get_education(key_word)
    info['echart_31'] = dao.get_fiance_stage(key_word)
    info['echart_32'] = dao.get_company_size(key_word)
    info['echart_33'] = dao.get_job_nature(key_word)
    info['map'] = dao.get_job_number_by_city(key_word)
    info['counter'] = dao.get_crawl_number(key_word)
    return jsonify(info)


# 获取首页词云图数据
@app.route("/get_word_clound/")
def get_word_clound():
    info = {}
    data = dao.query_hot_search()
    info['data'] = data
    return jsonify(info)


# 获取岗位福利词云图
@app.route("/get_position_label/<key_word>")
def get_position_label(key_word):
    info = {}
    info['word_clound'] = dao.get_company_label(key_word)
    info['bubble_chart'] = dao.get_position_num_and_avg_salary_by_city(key_word)
    return render_template("position_label.html", key_word=key_word, data=json.dumps(info))


# 错误处理
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=80)
