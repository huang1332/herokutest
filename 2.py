params = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/76.0.3809.132 Safari/537.36',
    'authority': 'www.pixiv.net',
    'content-type': 'application/x-www-form-urlencoded',
    'accept-language': 'zh-CN;q=0.9,zh;q=0.8,zh-TW;q=0.7,en-US,en;q=0.6,ja;q=0.6',
    'dnt': '1',
    'referer': 'https://www.pixiv.net/'
}
import grequests
from bs4 import BeautifulSoup
import demjson
import requests
s=  requests.session() 
req = s.get(r'https://www.pixiv.net/artworks/87093961' , headers=params)
new_soup = BeautifulSoup( req .text,'html.parser')
json_data = new_soup.find(name='meta',attrs={'name':'preload-data'}).attrs['content']
format_json_data = demjson.decode(json_data)
pre_catch_id = list(format_json_data['illust'].keys())[0]
print(pre_catch_id )
