import json
import random

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

#02 根据json里提供的链接爬取文章内容

def scrape_article_content(article):
    base_url = "https://www.zaobao.com.sg"
    full_url = base_url + article['href']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(full_url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch {full_url}: Status code {response.status_code}")
            return "Failed to fetch content"

        soup = BeautifulSoup(response.text, 'html.parser')
        article_body = soup.find('div', class_='articleBody')
        if not article_body:
            print(f"No article body found in {full_url}")
            return "No content found"

        content = []
        for elem in article_body.find_all(['p', 'h1', 'h2', 'h3'], recursive=True):
            if elem.name == 'p' and elem.text.strip() and not elem.find_parent('div', class_='paywall-container'):
                content.append(elem.text.strip())

        return "\n".join(content)

    except Exception as e:
        print(f"Error scraping {full_url}: {str(e)}")
        return "Error scraping content"


def main(input_json='files/zaobao_taiwan_articles.json',
         output_dir='.',
         start_idx=1,
         end_idx=None):
    # 读取 JSON
    with open(input_json, 'r', encoding='utf-8') as f:
        articles = json.load(f)

    total_articles = len(articles)
    print(f"总共有 {total_articles} 篇文章")

    # 默认 end_idx 为最后一篇
    if end_idx is None or end_idx > total_articles:
        end_idx = total_articles

    # 取区间
    articles_to_crawl = articles[start_idx - 1:end_idx]
    print(f"将爬取第 {start_idx} 篇 到 第 {end_idx} 篇，共 {len(articles_to_crawl)} 篇文章")

    # 生成文件名
    output_excel = os.path.join(output_dir, f"files/TH_zaobao/TH_zaobao_news_data_{start_idx}_{end_idx}.xlsx")

    # 爬取
    data = []
    for i, article in enumerate(articles_to_crawl, start=start_idx):
        article_id = f"TH2024_{i:03d}"
        content = scrape_article_content(article)
        data.append({
            'id': article_id,
            'content': content,
            'title': article['title'],
            'time': article['date']
        })
        print(f"已爬取第 {i} 篇，时间: {article['date']}，标题: {article['title']}")
        time.sleep(random.uniform(2,4))

    # 保存
    df = pd.DataFrame(data)
    df.to_excel(output_excel, index=False, engine='xlsxwriter')
    print(f"Data saved to {output_excel}")


if __name__ == "__main__":
    # 爬取第 x 到 y 篇
    # start_idx从1开始（总共有 352 篇文章）
    main(start_idx=281, end_idx=352)
    # main(start_idx=1)  # 这样就是爬取 1 到最后
