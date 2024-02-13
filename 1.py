from twitterscraper import query_tweets#name-twitterscraper
from openpyxl import Workbook#name-openpyxl

# 搜索用户的推文，不使用代理
tweets = query_tweets("from:gugugulee", limit=15, proxy=None)

# 创建工作簿和工作表
wb = Workbook()
ws = wb.active

# 添加表头
ws.append(['Timestamp', 'Username', 'Text', 'Media'])

# 遍历推文并写入工作表和输出至终端
for tweet in tweets:
    media_urls = ', '.join([media['expanded_url'] for media in tweet.media]) if tweet.media else ''
    row_data = [tweet.timestamp, tweet.username, tweet.text, media_urls]
    ws.append(row_data)
    print(f'Timestamp: {row_data[0]}, Username: {row_data[1]}, Text: {row_data[2]} 媒体链接: {row_data[3]} ٩(◕‿◕｡)۶')

# 指定保存的Excel文件名
excel_file = "gugugulee_tweets.xlsx"

# 保存工作簿至Excel文件
wb.save(excel_file)

print(f'推文和媒体链接已保存至 {excel_file} 文件中！')
