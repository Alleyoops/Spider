# -*- coding: utf-8 -*-
"""
路透社 Hegseth 搜索 - 断点续爬版（每次只爬一页，永不丢失）
手动设置 offset，爬完一页自动保存并退出
"""

import os
import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ==================== 配置区（你只需要改这里） ====================
# BASE_URL = "https://www.reuters.com/site-search/?query=Hegseth&date=past_year&sort=relevance"
# BASE_URL = "https://www.reuters.com/site-search/?query=Taiwan+Strait&sort=relevance&date=past_year"
BASE_URL = "https://www.reuters.com/site-search/?query=taiwan+us&date=past_year&sort=relevance"
BASE_URL = "https://www.reuters.com/site-search/?query=taiwan+eu&date=past_year&sort=relevance"
OFFSET = 40  # 你想从第几条开始？0、20、40、60... 手动改这里。（0代表第一页，20代表第二页，每页20条）
PAGE_SIZE = 20  # 固定20条，别改
# OUTPUT_DIR = "reuters_hegseth_数据包"  # 所有文件都会保存在这个文件夹
# OUTPUT_DIR = "reuters_TaiwanStrait_数据包"
OUTPUT_DIR = "reuters_TaiwanEU_数据包"

# 自动创建文件夹
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 输出文件名：每页一个文件 + 总合并文件
PAGE_FILE = os.path.join(OUTPUT_DIR, f"offset_{OFFSET}.xlsx")
# TOTAL_FILE = os.path.join(OUTPUT_DIR, "【总表】reuters_hegseth_all.xlsx")
# TOTAL_FILE = os.path.join(OUTPUT_DIR, "【总表】reuters_TaiwanStrait_all.xlsx")
TOTAL_FILE = os.path.join(OUTPUT_DIR, "【总表】reuters_TaiwanEU_all.xlsx")

# ===================================================================

def get_driver():
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Edge(options=options)
    return driver


def parse_list_page(driver):
    wait = WebDriverWait(driver, random.uniform(15, 20))
    cards = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//li[@data-testid='StoryCard']")))
    results = []

    for card in cards:
        try:
            a = card.find_element(By.XPATH, ".//a[@data-testid='TitleLink']")
            title = a.text.strip()
            link = a.get_attribute("href")

            time_tag = card.find_element(By.XPATH, ".//time[@data-testid='DateLineText']")
            date_raw = time_tag.get_attribute("datetime") or time_tag.text.strip()
            date = date_raw.split("T")[0] if "T" in date_raw else date_raw.split()[0] if date_raw else "Unknown"

            results.append({"date": date, "title": title, "link": link, "content": ""})
        except:
            continue
    print(f"   本页解析到 {len(results)} 条新闻链接")
    return results


def get_article_content(driver, url):
    try:
        driver.get(url)
        wait = WebDriverWait(driver, random.uniform(10, 15))

        # 主方案：2025最新结构
        paragraphs = driver.find_elements(By.XPATH, "//div[starts-with(@data-testid, 'paragraph-')]")
        texts = [p.text.strip() for p in paragraphs if p.text.strip()]

        # 备用方案
        if not texts:
            paragraphs = driver.find_elements(By.CSS_SELECTOR, "div.article-body__content__17Yit p")
            texts = [p.text.strip() for p in paragraphs if p.text.strip()]

        content = "\n\n".join(texts)
        return content if content else "（正文为空）"
    except Exception as e:
        return f"（读取失败：{str(e)[:50]}）"


# ==================== 主程序（只爬一页） ====================
print(f"正在接管 Edge 浏览器，开始爬取 offset={OFFSET} 的这一页（共{PAGE_SIZE}条）\n")

try:
    driver = get_driver()
except Exception as e:
    print("连接 Edge 失败！请先运行下面这行命令打开 Edge：")
    print(
        ' "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe" --remote-debugging-port=9222 --user-data-dir="C:\\edge-temp" ')
    input("打开后按回车继续...")
    driver = get_driver()

url = f"{BASE_URL}&offset={OFFSET}"
print(f"正在打开：{url}")
driver.get(url)
time.sleep(4)

articles = parse_list_page(driver)

# 逐条提取正文
for i, art in enumerate(articles, 1):
    print(f"   [{i:2d}/{len(articles)}] 正在读取正文：{art['title'][:60]}...")
    art["content"] = get_article_content(driver, art["link"])
    time.sleep(random.uniform(5, 10))

driver.quit()

# 保存本页结果
df_page = pd.DataFrame(articles)
df_page.to_excel(PAGE_FILE, index=False, engine="openpyxl")
print(f"\n本页爬取完成！已保存：{PAGE_FILE}")

# 合并到总表（自动去重）
if os.path.exists(TOTAL_FILE):
    df_total = pd.read_excel(TOTAL_FILE)
    df_combined = pd.concat([df_total, df_page], ignore_index=True)
    df_combined.drop_duplicates(subset=["link"], keep="last", inplace=True)  # 按链接去重
else:
    df_combined = df_page

df_combined["date"] = pd.to_datetime(df_combined["date"], errors="coerce")
df_combined = df_combined.sort_values("date", ascending=False).reset_index(drop=True)
df_combined.to_excel(TOTAL_FILE, index=False, engine="openpyxl")

print(f"已更新总表：{TOTAL_FILE}")
print(f"当前总计：{len(df_combined)} 条新闻")
print(f"\n下一页请把脚本中 OFFSET 改为 {OFFSET + 20} 继续运行即可")

input("\n任务完成，按回车退出程序...")