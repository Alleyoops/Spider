import requests
import time
from datetime import datetime, timezone

#01: 从【台海局势】专题获取所有相关新闻列表

def scrape_zaobao_taiwan_pages(start_page=0, end_page=21):
    base_url = "https://www.zaobao.com.sg/_plat/api/v2/page-content/special/taiwan?page={}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36'}
    all_articles = []

    for page in range(start_page, end_page + 1):
        url = base_url.format(page)
        print(f"Scraping page {page}: {url}")

        try:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                print(f"Failed to fetch page {page}: Status code {response.status_code}")
                continue

            data = response.json()
            if data.get("code") != 200 or not data.get("response", {}).get("articles"):
                print(f"No articles or invalid response on page {page}")
                continue

            # Filter articles with category_label == "news_china"
            for article in data["response"]["articles"]:
                if article.get("category_label") == "news_china":
                    # Convert timestamp to YYYY/M/D (e.g., 2024/1/2)
                    timestamp = article.get("timestamp")
                    if timestamp:
                        # Use timezone-aware UTC timestamp
                        date_obj = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                        # Format as YYYY/M/D, removing leading zeros
                        date_str = date_obj.strftime('%Y/%m/%d').replace('/0', '/')
                    else:
                        date_str = "N/A"

                    article_data = {
                        "title": article.get("title", "No Title"),
                        "href": article.get("href", ""),
                        "date": date_str
                    }
                    print(
                        f"Date: {date_str}, Title: {article.get('title', 'No Title')}, Link: {article.get('href', '')}"
                    )
                    all_articles.append(article_data)

        except Exception as e:
            print(f"Error on page {page}: {str(e)}")
            continue

        time.sleep(1)  # Respectful delay to avoid rate limiting

    return all_articles


# Execute the scraper
if __name__ == "__main__":
    # 从第七页开始抓取，只统计2024年的新闻
    articles = scrape_zaobao_taiwan_pages(7, 21)
    print(f"Total articles collected: {len(articles)}")
    # for article in articles:
    #     print(f"Date: {article['date']}, Title: {article['title']}, Link: {article['href']}")

    # Optional: Save to a file for further processing
    import json
    import os

    os.makedirs("files", exist_ok=True)

    with open("files/zaobao_taiwan_articles.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)