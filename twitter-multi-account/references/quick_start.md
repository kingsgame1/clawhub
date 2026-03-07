# Twitter 多账户管理快速开始

## 推荐方案

### 方案 1: Tweepy（Python 库）

```python
import tweepy

# API v2
client = tweepy.Client(
    bearer_token="YOUR_BEARER_TOKEN",
    consumer_key="YOUR_API_KEY",
    consumer_secret="YOUR_API_SECRET",
    access_token="YOUR_ACCESS_TOKEN",
    access_token_secret="YOUR_ACCESS_TOKEN_SECRET"
)

# 发帖
client.create_tweet(text="Hello, Twitter!")
```

### 方案 2: Playwright（浏览器自动化）

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://twitter.com")
    # 登录逻辑...

    # 发帖
    page.click('[data-testid="tweetTextarea_0"]')
    page.fill('[data-testid="tweetTextarea_0"]', "Hello, world!")
    page.click('[data-testid="tweetButton"]')
```

## 反检测策略

1. **随机延迟**: 30-60 秒
2. **模仿人类行为**: 滚动、点赞等
3. **IP 轮换**: 使用住宅代理
4. **账户年龄**: 新账号避免大操作

## 推荐 API

- Tweepy: https://docs.tweepy.org
- Playwright: https://playwright.dev/python
- Selenium: https://selenium.dev
