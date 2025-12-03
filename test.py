from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options

options = Options()
options.add_argument("--start-maximized")
service = Service("./msedgedriver.exe")   # 必须同目录
driver = webdriver.Edge(service=service, options=options)

driver.get("https://www.reuters.com")
print("成功打开路透社！标题是：", driver.title)
input("按回车关闭浏览器...")
driver.quit()