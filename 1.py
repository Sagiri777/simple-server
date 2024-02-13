import snscrape.modules.twitter as sntwitter
from openpyxl import Workbook

# 获取用户"gugugulee"的最近15条推文
tweets = sntwitter.TwitterUserScraper('gugugulee').get_items()

# 创建工作簿和工作表
wb = Workbook()
ws = wb.active

# 添加表头
ws.append(['Timestamp', 'Username', 'Text', 'Media'])

# 遍历推文并写入工作表
for tweet in tweets:
    media_urls = ', '.join([media.url for media in tweet.media]) if tweet.media else ''
    ws.append([tweet.date, tweet.user.username, tweet.content, media_urls])

# 指定保存的Excel文件名
excel_file = "gugugulee_tweets_snscrape_openpyxl.xlsx"

# 保存工作簿至Excel文件
wb.save(excel_file)

print(f'推文和媒体链接已保存至 {excel_file} 文件中！')
