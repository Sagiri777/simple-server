import os
import requests
import json
import get_time
from loghelper import log

# 获取 GitHub Secrets 中的 Cookie 和企业微信机器人 API Key 信息
baidu_cookie = os.environ.get('BAIDU_COOKIE', '')
wechat_bot_api_key = os.environ.get('WECHAT_BOT_API_KEY', '')

def get_history_events():
    # 获取当前日期信息
    date_parts = get_time.gettime()
    smonth, sday, year, month, day = date_parts

    date_str = smonth + sday

    # 百度百科历史上的今天 API URL
    api_url = f'https://baike.baidu.com/cms/home/eventsOnHistory/{smonth}.json'
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1 Edg/97.0.4692.99",
        "Cookie": baidu_cookie,
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://baike.baidu.com/calendar/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }
    r = requests.get(url=api_url, headers=headers)
    log.info('正在获取历史上的今天信息')
    j = json.loads(r.text)

    # 提取历史事件信息
    events_for_month = j[smonth]
    events_for_date = events_for_month[date_str]
    history_content = f"今天是{year}年{month}月{day}日\n历史上{month}月{day}日发生了这些事:\n"

    for event in reversed(events_for_date):
        title = event['title']
        year_event = event['year']
        desc = event['desc']
        festival = event['festival']
        event_type = event['type']
        history_content += f'{year_event}年{title}\n'

    log.info('获取完成！')

    # 将历史事件保存到文件（覆盖已存在文件）
    save_to_file(history_content, f'daily-history/{year}-{month}-{day}.txt')

    return history_content

def save_to_file(content, filename):
    # 文件保存路径
    result_folder = 'utils-results'
    daily_history_folder = 'daily-history'
    file_path = os.path.join(result_folder, daily_history_folder, filename)

    # 确保目录存在
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # 写入历史事件内容到文件
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def send_to_wechat(history_content):
    # 企业微信机器人推送
    wechat_url = f'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={wechat_bot_api_key}'
    headers = {'Content-Type': 'application/json'}

    payload = {
        "msgtype": "text",
        "text": {
            "content": history_content
        }
    }

    requests.post(wechat_url, headers=headers, data=json.dumps(payload))

if __name__ == '__main__':
    history_events = get_history_events()

    if history_events:
        send_to_wechat(history_events)
        print("历史上的今天推送成功！")
    else:
        print("无法获取历史事件。")
