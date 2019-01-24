from flask import Flask, jsonify, request  # simple server
import datetime
import os

app = Flask(__name__)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/phantomv/Downloads/sephora-interview-229603-c9967bbe7ccd.json"


@app.route('/')
def default():
    with open('front.html', 'rb') as f:
        html_content = f.read()
    return html_content


@app.route('/css')
def css():
    with open('css.css', 'rb') as f:
        html_content = f.read()
    return html_content


@app.route('/query', methods=['GET'])
def query():
    try:
        content = request.values
        for k in content:
            print(k, ':', content[k])

        from google.cloud import bigquery

        client = bigquery.Client()
        _h = lambda x: x + " like '%" + content[x] + "%'  " if content[x] != '' else ''
        _add_day = lambda x: (datetime.datetime.strptime(x, '%Y-%m-%d') + datetime.timedelta(days=1)).strftime(
            '%Y-%m-%d')
        title = _h('title')
        text = _h('text')
        time = "time_ts<'{}' and time_ts>='{}'".format(_add_day(content['date']), content['date']) if \
            content['date'] != '' else ''

        where = '' if title != '' and text != '' and time != '' else 'where '
        arg = ' and '.join(list(filter(lambda x: x != '', [title, text, time])))

        query_s = """
            SELECT title,url,text,time_ts
            FROM `bigquery-public-data.hacker_news.stories`
            {}{}
            limit 10
        """.format(where, arg)

        query_job = client.query(query_s)

        results = query_job.result()  # Waits for job to complete.

        post_resp = {}
        for i, v in enumerate(results):
            ele = {}
            for k in list(v.keys()):
                ele[k] = v[k]
            post_resp[i] = ele
        return jsonify(post_resp)
    except Exception as e:
        print(str(e))
        return str(e)


if __name__ == "__main__":
    app.run(host=app.config.get("HOST", "localhost"), port=app.config.get("PORT", 8000))
