# Playwright Scraper Skill ️
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![Playwright](https://img.shields.io/badge/Playwright-1.40+-blue.svg)](https://playwright.dev/)

基於 Playwright 的網頁爬蟲 OpenClaw Skill.支援反爬保護,已驗證成功爬取 Discuss.com.hk 等複雜網站.

> **安裝方法:** 查看 [INSTALL.md](INSTALL.md)
> **完整文件:** 查看 [SKILL.md](SKILL.md)
> **使用範例:** 查看 [examples/README.md](examples/README.md)

---

## 特色
- **純 Playwright** — 現代,強大,易用
- **反爬保護** — 隱藏自動化特徵,真實 UA
- **已驗證** — Discuss.com.hk 100% 成功
- **簡單易用** — 一行命令搞定
- **可自訂** — 支援環境變數配置

## 快速開始

### 安裝
```bash
npm install
npx playwright install chromium
```

# 快速爬取
node scripts/playwright-simple.js https://example.com

# 反爬保護版(推薦)
node scripts/playwright-stealth.js "https://m.discuss.com.hk/#hot"

## 兩種模式
**Simple**, 適用場景=一般動態網站, 速度=快(3-5秒), 反爬能力=無
**Stealth** ⭐, 適用場景=有反爬保護的網站, 速度=中(5-20秒), 反爬能力=中高

### Simple 模式
適合沒有反爬保護的網站:

node scripts/playwright-simple.js <URL>

### Stealth 模式(推薦)
適合有 Cloudflare 或反爬保護的網站:

node scripts/playwright-stealth.js <URL>

**反爬技巧:**
- 隱藏 `navigator.webdriver`, 真實 User-Agent(iPhone), 模擬真人行為, 支援截圖和 HTML 儲存

## 自訂參數
所有腳本都支援環境變數:

# 顯示瀏覽器
HEADLESS=false node scripts/playwright-stealth.js <URL>

# 自訂等待時間(毫秒)
WAIT_TIME=10000 node scripts/playwright-stealth.js <URL>

# 儲存截圖
SCREENSHOT_PATH=/tmp/page.png node scripts/playwright-stealth.js <URL>

# 儲存 HTML
SAVE_HTML=true node scripts/playwright-stealth.js <URL>

# 自訂 User-Agent
USER_AGENT="Mozilla/5.0 ..." node scripts/playwright-stealth.js <URL>

## 測試結果
**Discuss.com.hk**, 結果= 200 OK, 時間=5-20 秒
**Example.com**, 結果= 200 OK, 時間=3-5 秒
**Cloudflare 保護網站**, 結果= 多數成功, 時間=10-30 秒

## 檔案結構
playwright-scraper-skill/
├── scripts/
│ ├── playwright-simple.js # 簡單版
│ └── playwright-stealth.js # Stealth 版 ⭐
├── examples/
│ ├── discuss-hk.sh # Discuss.com.hk 範例
│ └── README.md # 更多範例
├── SKILL.md # 完整文件
├── INSTALL.md # 安裝指南
├── README.md # 本檔案
├── CONTRIBUTING.md # 貢獻指南
├── CHANGELOG.md # 版本記錄
└── package.json # npm 配置

## 使用建議
1. **先試 web_fetch** — OpenClaw 內建工具最快
2. **動態網站用 Simple** — 沒有反爬保護時
3. **反爬網站用 Stealth** ⭐ — 主力工具
4. **特殊網站用專用 skill** — YouTube,Reddit 等

## 故障排除

### 被 403 擋住?
使用 Stealth 模式:

### Cloudflare 挑戰?
增加等待時間 + 有頭模式:
HEADLESS=false WAIT_TIME=30000 node scripts/playwright-stealth.js <URL>

### 找不到 Playwright?
重新安裝:

更多問題查看 [INSTALL.md](INSTALL.md)

## 貢獻
歡迎貢獻!查看 [CONTRIBUTING.md](CONTRIBUTING.md)

## 授權
MIT License - 查看 [LICENSE](LICENSE)

## 相關連結
- [Playwright 官方文檔](https://playwright.dev/), [完整文件 (SKILL.md)](SKILL.md), [安裝指南 (INSTALL.md)](INSTALL.md), [使用範例 (examples/)](examples/)