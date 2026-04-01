# CSDN博客爬虫

一个用于批量下载CSDN博客文章并转换为多种格式（HTML、PDF、Markdown）的Python工具。

## 功能特点

- **批量下载**: 爬取CSDN分类/博客页面的所有文章
- **多格式输出**: 将文章保存为HTML、PDF和Markdown三种格式
- **自动创建目录**: 自动创建输出文件夹
- **健壮的错误处理**: 即使部分文章下载失败，程序也会继续运行
- **SSL/TLS支持**: 使用urllib作为后备方案绕过SSL证书问题
- **智能PDF生成**: 自动检测wkhtmltopdf安装状态

## 安装步骤

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. wkhtmltopdf（已包含，无需额外安装）

项目已包含 wkhtmltopdf 工具（位于 `wkhtmltopdf/bin/` 目录），无需额外安装。脚本会自动检测并使用本地的 wkhtmltopdf。

如果需要更新或使用其他版本，可以从 [wkhtmltopdf官网](https://wkhtmltopdf.org/) 下载。

## 使用方法

### 基本使用

1. 编辑 `csdn.py` 中的目标URL（第75-77行）：

```python
def __init__(self):
    # self.url = 'https://blog.csdn.net/holden_liu/category_10656300.html'
    self.url = 'https://blog.csdn.net/你的目标博客/category_xxxxx.html'
    self.headers = {
        'user-agent': random.choice(USER_AGENT_LIST)
    }
```

2. 运行脚本：

```bash
python csdn.py
```

### 输出结构

```
scripts/csdn/
├── HTML/          # HTML格式文件
├── PDF/           # PDF格式文件（需要wkhtmltopdf）
└── MD/            # Markdown格式文件
```

## 工作原理

1. **获取分类页面**: 请求CSDN分类/博客列表页
2. **提取文章链接**: 从页面解析所有文章URL
3. **下载文章**: 获取每篇文章的完整内容
4. **格式转换**:
   - 保存原始HTML
   - 转换HTML为PDF（需要wkhtmltopdf）
   - 转换HTML为Markdown（使用html2text）
5. **错误恢复**: 即使单篇文章失败也会继续处理下一篇

## 配置说明

### 目标URL

修改 `CSDNSpider.__init__()` 方法中的 `self.url` 为你的目标CSDN分类页面。

示例URL：
- 分类页面：`https://blog.csdn.net/用户名/category_12345.html`
- 博客首页：`https://blog.csdn.net/用户名/`

### User-Agent轮换

脚本使用预定义的User-Agent字符串列表来避免被屏蔽。你可以修改 `USER_AGENT_LIST`（第44-70行）来添加或更改代理。

## 常见问题解决

### SSL/TLS错误

如果遇到SSL错误，脚本会自动回退到使用`urllib`绕过SSL验证。这是内部处理的，无需手动干预。

### 521 HTTP错误

CSDN可能返回521错误（Cloudflare/服务器过载）。脚本会跳过失败的文章并继续处理其他文章。如果大量文章失败，只需重新运行脚本即可。

### PDF生成失败

- 项目已包含 wkhtmltopdf（位于 `wkhtmltopdf/bin/` 目录）
- 脚本会自动检测本地的 wkhtmltopdf：
  - `D:\LZYchangqishixi\scripts\csdn\wkhtmltopdf\bin\wkhtmltopdf.exe`
  - `C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe`
  - `C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe`
  - 或在系统PATH中的任何位置

### 权限错误

确保你对脚本目录有写入权限。脚本会自动创建 `HTML/`、`PDF/`、`MD/` 文件夹。

## 代码结构

```
CSDNSpider
├── __init__()           # 初始化URL和请求头
├── send_request()       # HTTP请求（带SSL后备方案）
├── parse_content()      # 从分类页提取文章链接
├── parse_detail()       # 从文章页提取标题和内容
├── write_content()      # 保存为HTML/PDF/MD格式
├── change_title()       # 文件名清理
└── start()              # 主入口
```

## 依赖包说明

| 包名 | 用途 |
|------|------|
| requests | HTTP请求（主要） |
| urllib | HTTP请求（SSL后备） |
| parsel | CSS选择器解析 |
| beautifulsoup4 | HTML解析 |
| pdfkit | HTML转PDF |
| html2text | HTML转Markdown |

## 法律与伦理说明

- 本工具仅用于**个人学习和备份**目的
- 请遵守CSDN的服务条款和robots.txt协议
- 勿用于商业目的
- 如需修改高频请求，请添加适当的延迟
- 建议支持原创作者，访问其博客原文

## 局限性

- **频率限制**: 没有内置请求延迟（如需请添加 `time.sleep()`）
- **登录限制**: 需要登录的私有文章无法访问
- **动态内容**: JavaScript渲染的内容可能无法捕获
- **PDF质量**: PDF转换质量取决于wkhtmltopdf的渲染能力

## 自定义扩展

### 添加请求延迟

为避免被屏蔽，在 `parse_content()` 中添加延迟：

```python
import time

def parse_content(self, reponse):
    # ... 现有代码 ...
    for link in href:
        time.sleep(1)  # 添加1秒延迟
        # ... 其余代码 ...
```

### 只保存特定格式

修改 `write_content()` 只保存需要的格式：

```python
def write_content(self, content, name):
    # 只保存HTML
    with open(f"HTML/{name}.html", 'w', encoding="utf-8") as f:
        f.write(content)
```

### 添加代理支持

在 `send_request()` 中添加代理配置：

```python
proxies = {
    'http': 'http://你的代理:端口',
    'https': 'https://你的代理:端口'
}
response = requests.get(url=url, headers=self.headers, verify=False, proxies=proxies, timeout=10)
```

## 许可证

本项目仅供学习研究使用。请遵守相关法律法规。

## 作者信息

原作者：survive
博客：https://blog.csdn.net/haojie_duan
座右铭："我不知道将去何方，但我已在路上。——宫崎骏《千与千寻》"

---

**最后更新**: 2026-04-01
**Python版本**: 3.9+
**支持平台**: Windows/Linux/macOS
**项目位置**: D:\LZYchangqishixi\scripts\csdn
