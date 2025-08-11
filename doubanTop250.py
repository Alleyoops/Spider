import json
import time

import requests
from bs4 import BeautifulSoup

url = 'https://movie.douban.com/top250'
# 伪装浏览器
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.google.com/',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Connection': 'keep-alive'
}

'''
response.text 是 str 类型，它是根据 response.encoding 解码后的字符串。
response.content 是 bytes 类型，是原始的二进制响应内容，不会出现乱码问题，适合用于图片、文件等二进制数据。
'''
# 结构化打印response.headers(CaseInsensitiveDict转dict在转为json并打印json格式的str)
'''
特性	            JSON	        Python 字典
类型	            字符串格式（文本）	内存中的数据结构
键/值引号	    必须双引号 " "	单/双引号均可
数据类型支持	    仅基本类型	    所有 Python 类型
用途	            跨语言数据交换	程序内部数据处理
'''


''' 
如果服务器返回的是 Brotli（br）或 zstd 压缩格式，
而你的环境中没有安装相应的解压库，会导致 requests 无法正确解压响应内容，
从而 .text 出现乱码。
'''


movies = []
# 1、查找所有电影标题（豆瓣 Top250 页面中，电影名在 <span class="title"> 中）
def extract_movie_info(item):
    # 提取电影名称
    name_tag = item.select_one('.title')
    name = name_tag.text.strip() if name_tag else '未知'

    # 提取导演
    bd_p = item.select_one('.bd > p')
    director = '未知'
    if bd_p:
        text = bd_p.get_text()
        if '导演: ' in text:
            director = text.split('导演: ')[1].split(' ')[0]

    # 提取语录
    quote_tag = item.select_one('.quote span')
    intro = quote_tag.text.strip() if quote_tag else '暂无简介'
    # 返回电影信息(字典)
    return {
        'name': name,
        'director': director,
        'intro': intro
    }

# 翻页
for i in range(0, 10):
    start = i * 25
    url = f'https://movie.douban.com/top250?start={start}&filter='
    print(f'正在抓取第 {i + 1} 页：{url}')
    response = requests.get(url, headers=headers)
    # 设置编码
    response.encoding = 'utf-8'
    # 解析html文本（str）
    # print(json.dumps(dict(response.headers), indent=4,ensure_ascii=False))
    text = response.text
    # 对html进行解析，提取电影名称（中文）、导演和简介
    soup = BeautifulSoup(text, 'html.parser')
    for item in soup.select('div.item'):
        movie_data = extract_movie_info(item)
        movies.append(movie_data)
    # 延时防止被封 IP
    time.sleep(1)

# 格式化打印movie
n = 1
for movie in movies:
    print('No.'+ str(n) + ':')
    print(f"电影名称：{movie['name']}")
    print(f"导演：{movie['director']}")
    print(f"简介：{movie['intro']}")
    print('-' * 30)
    n+=1
# 保存movie到files目录下的文件
with open('files/movies.json', 'w', encoding='utf-8') as f:
    json.dump(movies, f, ensure_ascii=False, indent=4)
    print('保存成功！')
