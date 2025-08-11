import os
import random

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import openpyxl
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time


'''
tip：朴实无华但稳定
'''
# 初始化 ID 起始值
current_id = 000  # 对应 TH2024_001

# 创建 Excel 工作簿和工作表
wb = openpyxl.Workbook()
ws = wb.active
ws.append(['id', 'content', 'title', 'time'])  # 表头

# 配置 Selenium 浏览器选项
chrome_options = Options()
# chrome_options.add_argument('--headless')  # 无头模式（可选）(浏览器页面可见，更真实)
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('blink-settings=imagesEnabled=false')  # 禁止图片加载
chrome_options.add_argument(
    'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
)

# 设置 WebDriver 路径（请替换为你的 chromedriver 路径）
service = Service(executable_path='chromedriver.exe')

# 初始化浏览器
driver = webdriver.Chrome(service=service, options=chrome_options)

from selenium.webdriver.common.action_chains import ActionChains
import random

#添加随机滚动、鼠标移动和刷新操作，模仿人类用户
def simulate_human_behavior(driver):
    try:
        # 随机滚动页面
        driver.execute_script(f"window.scrollTo(0, {random.randint(100, 500)});")
        time.sleep(random.uniform(0.5, 1.5))
        # 模拟鼠标移动
        ActionChains(driver).move_by_offset(random.randint(10, 50), random.randint(10, 50)).perform()
        time.sleep(random.uniform(0.5, 1))
        # 模拟刷新
        driver.refresh()
        time.sleep(random.uniform(3, 5))
    except Exception as e:
        print(f"模拟人类行为失败: {e}")

def crawl_page_with_selenium(url, max_retries=3):
    """
    爬取新闻列表页，获取链接、标题、发布时间
    支持重试，items为空时加长等待时间重试，最多max_retries次
    """
    wait_time_base = 12  # 初始等待时间
    retry = 0

    while retry < max_retries:
        driver.get(url)
        simulate_human_behavior(driver)
        wait_time = random.uniform(wait_time_base + retry * 5, wait_time_base + (retry+1) * 5)  # 递增等待时间
        print(f"等待页面加载 {wait_time:.1f} 秒（第{retry+1}次尝试）")
        time.sleep(wait_time)  # 等待页面加载完成

        items = driver.find_elements(By.CSS_SELECTOR, ".content .items  .item")
        print(f"本次尝试找到items数量: {len(items)}")
        # print(driver.page_source)

        if items:  # 非空则继续处理
            news_list = []
            for item in items:
                try:
                    a_tag = item.find_element(By.CSS_SELECTOR, ".title a")
                    title = a_tag.text.strip()
                    link = a_tag.get_attribute("href")

                    time_elem = item.find_element(By.CSS_SELECTOR, ".pub-tim")
                    pub_time = time_elem.text.strip() if time_elem else "未知时间"

                    if " " in pub_time:
                        date_str = pub_time.split(" ")[0]
                        year, month, day = date_str.split("-")
                        formatted_time = f"{int(year)}/{int(month)}/{int(day)}"
                    else:
                        formatted_time = pub_time

                    news_list.append({
                        'link': link,
                        'title': title,
                        'time': formatted_time
                    })

                    print(f"已获取新闻: {title} - {link} （发布时间：{formatted_time}）")
                except Exception as e:
                    print(f"提取失败: {e}")

            return news_list

        else:
            retry += 1

    # 三次都失败，返回空列表
    print(f"警告：连续{max_retries}次尝试都未找到items，跳过该页：{url}")
    return []

# def crawl_page_with_selenium(url):
#     """
#     爬取新闻列表页，获取链接、标题、发布时间
#     """
#     driver.get(url)
#     wait_time = random.uniform(15,20)
#     time.sleep(wait_time)  # 等待页面加载完成
#
#     news_list = []
#     items = driver.find_elements(By.CSS_SELECTOR, ".content .items  .item")
#     # items = WebDriverWait(driver, 15).until(
#     #     EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".content .items  .item"))
#     # )
#     if len(items)==0:
#         print("items为空，可能的失败原因：等待页面动态加载指定元素的时间较短，请重试或加长随机等待时间")
#     else:
#         print("本页成功提取到新闻数量："+ len(items))
#     for item in items:
#         try:
#             # 提取标题与链接
#             a_tag = item.find_element(By.CSS_SELECTOR, ".title a")
#             title = a_tag.text.strip()
#             link = a_tag.get_attribute("href")
#
#             # 提取时间
#             time_elem = item.find_element(By.CSS_SELECTOR, ".pub-tim")
#             pub_time = time_elem.text.strip() if time_elem else "未知时间"
#
#
#             # 时间格式转换：如 "2025-07-15 16:58:24" -> "2025/7/15"
#             if " " in pub_time:
#                 date_str = pub_time.split(" ")[0]
#                 year, month, day = date_str.split("-")
#                 formatted_time = f"{int(year)}/{int(month)}/{int(day)}"
#             else:
#                 formatted_time = pub_time
#
#             news_list.append({
#                 'link': link,
#                 'title': title,
#                 'time': formatted_time
#             })
#
#             print(f"已获取新闻: {title} - {link} （发布时间：{formatted_time}）")
#
#         except Exception as e:
#             print(f"提取失败: {e}")
#
#     return news_list


def get_news_content(url):
    """
    获取新闻详情页正文内容（适配新华网不同页面结构）
    """
    driver.get(url)
    wait_time = random.uniform(3, 7)
    time.sleep(wait_time)

    # 可能的正文定位规则
    selectors = [
        (By.ID, "detailContent"),   # 原规则 1
        (By.ID, "detail"),          # 原规则 2
        (By.CLASS_NAME, "detail"),  # 常见 class
        (By.CLASS_NAME, "p-detail"),
        (By.CLASS_NAME, "main-content"),
        (By.CLASS_NAME, "article")  # 新增规则，适配 class="article"
    ]

    for by, value in selectors:
        try:
            content_elem = driver.find_element(by, value)
            text = content_elem.text.strip()
            if text:  # 确保不是空字符串
                return text
        except:
            continue

    print(f"[警告] 无法提取正文: {url}")
    return ""


def main():
    global current_id
    base_url = (
        "https://so.news.cn/?keyWordAll=%E8%B5%96%E5%BE%B7%E6%B8%85&keyWordOne=%E8%B5%96%E5%BE%B7%E6%B8%85+"
        "%E5%8F%B0%E6%B9%BE+%E5%8F%B0%E6%B5%B7+%E5%8F%8D%E5%88%B6+%E5%86%9B%E6%BC%94+%E6%BC%94%E4%B9%A0"
        "&searchFields=0&sortField=0&lang=cn&senSearch=1"
        "#search/0/%E8%B5%96%E5%BE%B7%E6%B8%85")
    # 创建 files 文件夹（如果不存在）
    output_dir = "files"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 爬取第x页(赖清德，从22页开始爬取至97)
    # 总目标：_页
    file_name = os.path.join(output_dir, "TH_news_data_81_82.xlsx")
    for page in range(81, 83):
        url = f"{base_url}/{page}/0"
        print(f"\n正在爬取第{page}页: {url}")
        news_items = crawl_page_with_selenium(url)

        for item in news_items:
            print(f"正在抓取新闻: {item['title']} - {item['link']} （发布时间：{item['time']}）")
            content = get_news_content(item['link'])

            if content:
                current_id += 1
                news_id = f"TH2024_{str(current_id).zfill(3)}"
                ws.append([
                    news_id,
                    content,
                    item['title'],
                    item['time']
                ])

    # 保存 Excel 文件
    wb.save(file_name)
    print("\n数据已成功保存到"+file_name)


if __name__ == '__main__':
    try:
        main()
    finally:
        driver.quit()
