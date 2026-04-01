"""
@Author:survive
@Blog(个人博客地址): https://blog.csdn.net/haojie_duan
 
@File:csdn.py.py
@Time:2022/2/10 8:49
 
@Motto:我不知道将去何方，但我已在路上。——宫崎骏《千与千寻》

代码思路：
1.确定目标需求:将csdn文章内容保存成 html、PDF、md格式
    - 1.1首先保存为html格式：获取列表页中所有的文章ur1地址，请求文章ur1地址获取我们需要的文章内容
    - 1.2 通过 wkhtmitopdf.exe把html文件转换成PDF文件
    - 1.3 通过 wkhtmitopdf.exe把html文件转换成md文件

2.请求ur1获取网页源代码
3.解析数据，提取自己想要内容
4.保存数据
5.转换数据类型把HTML转换成PDF、md文伴
"""


html_str = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Document</title>
</head>
<body>
{article}
</body>
</html>
"""

import urllib.request
import urllib.parse
import urllib3
import ssl
import requests
import parsel
import pdfkit   #用来将html转为pdf
import re
import os
from bs4 import BeautifulSoup
import html2text    #用来将html转换为md
import random

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 创建全局SSL上下文，禁用证书验证
ssl_context = ssl._create_unverified_context()

# user_agent库：每次执行一次访问随机选取一个 user_agent，防止过于频繁访问被禁止
USER_AGENT_LIST = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36"
]

class CSDNSpider():
    def __init__(self):
        # self.url = 'https://blog.csdn.net/holden_liu/category_10656300.html'
        # 尝试使用HTTP而非HTTPS
        self.url = 'https://blog.csdn.net/weixin_43580890/category_12497553.html?orderBy=2'
        self.headers = {
            'user-agent':random.choice(USER_AGENT_LIST)
        }

    def send_request(self, url, retry=3, delay=2):
        """使用urllib发送请求，避免requests的SSL问题，并添加重试机制"""
        for i in range(retry):
            try:
                # 构建请求
                req = urllib.request.Request(url, headers=self.headers)
                # 发送请求，使用不验证SSL的上下文
                response = urllib.request.urlopen(req, context=ssl_context, timeout=15)
                # 读取并解码内容
                html = response.read().decode('utf-8')
                # 创建一个类似requests.Response的对象
                class FakeResponse:
                    def __init__(self, url, status, text):
                        self.url = url
                        self.status_code = status
                        self.text = text
                        self.content = text.encode('utf-8')
                        self.encoding = 'utf-8'
                    def raise_for_status(self):
                        if self.status_code >= 400:
                            raise Exception(f"HTTP Error {self.status_code}")
                return FakeResponse(response.geturl(), response.status, html)
            except Exception as e:
                print(f"Request failed for {url} (attempt {i+1}/{retry}): {e}")
                if i < retry - 1:
                    import time
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= 2  # 指数退避
                else:
                    print(f"All attempts failed for {url}")
        return None

    def parse_content(self, reponse):
        html = reponse.text
        selector = parsel.Selector(html)
        href = selector.css('.column_article_list a::attr(href)').getall()
        name = 0
        for link in href:
            print(link)
            name = name + 1
            # 添加随机延迟，避免请求过于频繁
            import time
            import random
            delay = random.uniform(1, 3)  # 随机延迟1-3秒
            print(f"Waiting {delay:.2f} seconds before next request...")
            time.sleep(delay)
            # 对文章的url地址发送请求
            response = self.send_request(link)
            if response:
                self.parse_detail(response, name)

    def parse_detail(self, response, name):
        html = response.text
        # print(html)
        selector = parsel.Selector(html)
        title = selector.css('#articleContentId::text').get()
        # content = selector.css('#content_views').get()

        # 由于这里使用parsel拿到的网页文件，打开会自动跳转到csdn首页，并且不能转为pdf，就想在这里用soup
        soup = BeautifulSoup(html, 'lxml')
        #content = soup.find('div',id="content_views",class_="markdown_views prism-atom-one-light" or "htmledit_views") #class_="htmledit_views"
        #为了提高兼容性，ReturnTmp 推荐将上一行代码改为下面三行，希望大家用得舒服
        content_markdown = soup.find('div', id="content_views", class_="markdown_views prism-atom-one-light")
        content_htmledit = soup.find('div', id="content_views", class_="htmledit_views")

        content = content_htmledit if content_htmledit is not None else content_markdown    

        # print(content)
        # print(title, content)
        html = html_str.format(article=content)
        self.write_content(html, title)

    def write_content(self, content, name):
        # 确保输出目录存在
        os.makedirs("HTML", exist_ok=True)
        os.makedirs("PDF", exist_ok=True)
        os.makedirs("MD", exist_ok=True)
        
        html_path = "HTML/" + str(self.change_title(name)) + ".html"
        pdf_path ="PDF/" + str(self.change_title(name))+ ".pdf"
        md_path = "MD/" + str(self.change_title(name)) + ".md"

        # 将内容保存为html文件
        with open(html_path, 'w',encoding="utf-8") as f:
            f.write(content)
            print("正在保存", name, ".html")

        # 将html文件转换成PDF文件（如果wkhtmltopdf可用）
        try:
            # 尝试自动查找wkhtmltopdf
            import shutil
            wkhtmltopdf_path = shutil.which('wkhtmltopdf')
            if wkhtmltopdf_path:
                config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
            else:
                # 常见安装路径
                common_paths = [
                    r'D:\LZYchangqishixi\scripts\csdn\wkhtmltopdf\bin\wkhtmltopdf.exe',
                    r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe',
                    r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe',
                ]
                for path in common_paths:
                    if os.path.exists(path):
                        config = pdfkit.configuration(wkhtmltopdf=path)
                        break
                else:
                    print("警告: 未找到wkhtmltopdf，跳过PDF生成")
                    return
            pdfkit.from_file(html_path, pdf_path, configuration=config)
            print("正在保存", name, ".pdf")
        except Exception as e:
            print(f"PDF转换失败: {e}")

        # 将html文件转换成md格式
        try:
            html_text = open(html_path, 'r', encoding='utf-8').read()
            markdown = html2text.html2text(html_text)
            with open(md_path, 'w', encoding='utf-8') as file:
                file.write(markdown)
                print("正在保存", name, ".md")
        except Exception as e:
            print(f"MD转换失败: {e}")

    def change_title(self, title):
        mode = re.compile(r'[\\\/\:\?\*\"\<\>\|\!]')
        new_title = re.sub(mode,'_', title)
        return new_title

    def start(self):
        print(f"正在访问: {self.url}")
        response = self.send_request(self.url)
        if response:
            print(f"成功获取页面，状态码: {response.status_code}")
            self.parse_content(response)
        else:
            print("无法访问目标页面，请检查：")
            print("1. URL是否正确且可访问")
            print("2. 网络连接是否正常")
            print("3. 是否需要登录CSDN才能访问该页面")


if __name__ == '__main__':
    csdn = CSDNSpider()
    csdn.start()
