

import asyncio
import json
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

# 输出文件
output_file = "professor_xt.json"
# 已访问的 URL 集合
visited_urls = set()


# 保存到文件
async def save_to_file(professor_info):
    with open(output_file, "a", encoding="utf-8") as file:
        file.write(json.dumps(professor_info, ensure_ascii=False) + ",\n")


# 格式化 JSON 输出
async def finalize_json_file():
    with open(output_file, "r", encoding="utf-8") as file:
        content = file.read().strip(",\n")
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(f"[{content}]")


# 抓取主页面的教师链接
async def main_page(page):
    content = await page.content()
    soup = BeautifulSoup(content, "html.parser")
    result_urls = []

    # 抓取教师链接
    for link in soup.select(
            "body > div.nymain > div.ny-c.px1400 > div.teacher > div.teacher-list > div.teacher-list a"):
        href = link.get("href")
        if href and href.startswith(".."):
            full_href = href.replace("../", "https://www.sice.uestc.edu.cn/")
            if full_href not in visited_urls:
                visited_urls.add(full_href)
                result_urls.append(full_href)

    print(f"抓取到的链接：{len(result_urls)} 个")
    return result_urls


# 抓取详细页面的教师信息
async def detail_page(page, url):
    try:
        await page.goto(url, timeout=60000)  # 设置超时时间
        content = await page.content()
        soup = BeautifulSoup(content, "html.parser")

        # 抓取教师信息
        name = soup.select_one("body > div.nymain > div.ny-c.px1400 > div > form > div.ti-tx > div.ti-info")
        name = name.get_text(strip=True) if name else ""

        introduction = soup.select_one(
            "body > div.nymain > div.ny-c.px1400 > div > form > div.ti-tx > div.ti-details > ul")
        introduction = introduction.get_text(strip=True) if introduction else ""

        professor_info = {
            "person": name,
            "introduction": introduction,
        }
        await save_to_file(professor_info)

    except Exception as e:
        print(f"抓取 {url} 时发生错误：{e}")


# 处理分页逻辑
async def handle_pagination(context,page):

    page_number = 2  # 从第 2 页开始
    while True:
        page_selector = f"#pagenyCaList > div > a:nth-child({page_number})"
        try:
            await page.wait_for_selector(page_selector, timeout=6000)
            print(f"正在切换到第 {page_number} 页...")

            # 点击分页按钮
            await page.click(page_selector)
            await page.wait_for_load_state("networkidle")  # 等待页面加载完成

            # 抓取新页面内容
            urls = await main_page(page)
            for url in urls:
                new_page = await context.new_page()  # 在浏览器上下文中打开新页面
                await new_page.goto(url)  # 在新页面中打开链接
                await detail_page(new_page, url)  # 抓取新页面内容
                await new_page.close()  # 处理完后关闭新页面

            page_number += 1
        except Exception as e:
            print(f"分页失败：无法加载第 {page_number} 页。错误：{e}")
            if page_number < 19:
                continue
            break


# 主函数
async def main():
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0'
    cookies = [
        {
            'name': 'zg_did',
            'value': '%7B%22did%22%3A%20%22192d88e893ce81-0cd7f80c1f8a1b-4c657b58-1fa400-192d88e893d1582%22%7D',
            'domain': 'www.scse.uestc.edu.cn',
            'path': '/'
        },
        {
            'name': 'zg_',
            'value': '%7B%22sid%22%3A%201730895559228%2C%22updated%22%3A%201730895559234%2C%22info%22%3A%201730890331425%2C%22superProperty%22%3A%20%22%7B%7D%22%2C%22platform%22%3A%20%22%7B%7D%22%2C%22utm%22%3A%20%22%7B%7D%22%2C%22referrerDomain%22%3A%20%22eportal.uestc.edu.cn%22%2C%22cuid%22%3A%20%22202322070221%22%2C%22zs%22%3A%200%2C%22sc%22%3A%200%2C%22firstScreen%22%3A%201730895559228%7D',
            'domain': 'www.scse.uestc.edu.cn',
            'path': '/'
        },
        {
            'name': 'JSESSIONID',
            'value': '3B71E7A36A681559C76D52D4FB0AB9A1',
            'domain': 'www.scse.uestc.edu.cn',
            'path': '/'
        }
    ]

    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=False)  # 设置 Firefox 浏览器

        context = await browser.new_context(
            user_agent=user_agent  # 设置 User-Agent
        )
        await context.add_cookies(cookies)  # 设置 cookies

        page = await context.new_page()

        # 打开主页面
        await page.goto('https://www.sice.uestc.edu.cn/szdw/jsml1.htm')

        # 等待主页面加载完成
        try:
            await page.wait_for_selector(
                'body > div.nymain > div.ny-c.px1400 > div.teacher > div.teacher-list > div.teacher-list',
                timeout=3000 # 设置较长的等待时间
            )
        except Exception as e:
            print(f"页面加载失败: {e}")
            await browser.close()
            return

        print("主页面加载完成!")

        # 抓取主页面的链接
        urls = await main_page(page)

        # 为每个链接打开新的页面
        for url in urls:
            new_page = await context.new_page()  # 在浏览器上下文中打开新页面
            await new_page.goto(url)  # 在新页面中打开链接
            await detail_page(new_page, url)  # 抓取新页面内容
            await new_page.close()  # 处理完后关闭新页面

        # 处理分页
        await handle_pagination(context, page)

        # 最终格式化 JSON 输出
        await finalize_json_file()

        await page.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())




