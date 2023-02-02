import requests
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 "
                  "Safari/537.36 "
}
COOKIE = {"cookies": "session=8b757a08-0c18-4db0-ab2f-7e6b9a291950.lXvWCJ0W-MIJw2YS-VvSaHUwwGE"}


def test_api(target_url, method='get', data=None, json_data=None):
    resp = None
    if not data:
        data = {}
    if method.upper() == 'GET':
        resp = requests.get(target_url, cookies=COOKIE, headers=HEADERS)
    if method.upper() == 'POST':
        resp = requests.post(target_url, data, json_data, cookies=COOKIE, headers=HEADERS)

    return resp


def test1():
    url = 'http://127.0.0.1:5000/sql_mapper/test'
    test_data = {
        "select": [{
            "column": "user_name", "group_func": "count", "cal_func": "round", "rel_column": "user_id",
            "rel_cal_func": "round", "relation_func": "/",
            "rename": "columns1"
        }, {
            "column": "user_name", "group_func": "count", "cal_func": "round", "rel_column": "user_id",
            "rel_cal_func": "round", "relation_func": "/",
            "rename": "columns2"
        }

        ],
        "target_table": "event",
        "where": [{
            "column": "level", "condition_type": ">", "condition": "1500"
        }],
        "group_by": ["user_name"],
        "having": [],
        "order_by": [],
        "limit": 1000
    }
    res = test_api(url, 'post', json_data=json.dumps(test_data))
    print(res.text)


def test2():
    url = 'http://127.0.0.1:5000/sql_mapper/mapper/mapper_executor'
    data = {
        'mapper_query': 'select count(1) from event;'
    }
    res = test_api(url, method='post', json_data=json.dumps(data))
    print(res.text)


if __name__ == '__main__':
    test2()
