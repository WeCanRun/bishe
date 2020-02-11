from flask import Flask, render_template, jsonify

from data_spider.insert_data import dao

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/get_echart_data",methods=['GET','POST'])
def get_echart_data():
    info = {}
    info['echart_1'] = dao.get_industryfield()
    info['echart_2'] = dao.get_salary()
    info['echart_4'] = dao.get_job_number_by_date()
    info['echart_5'] = dao.get_worker_year()
    info['echart_6'] = dao.get_education()
    info['echart_31'] = dao.get_fiance_stage()
    info['echart_32'] = dao.get_company_size()
    info['echart_33'] = dao.get_job_nature()
    info['map'] = dao.get_job_number_by_city()
    info['counter'] = dao.get_crawl_number()

    return jsonify(info)

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0", port=8080)