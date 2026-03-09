# Agent Browser Skill - 安装报告

## 安装状态
- **SKILL.md**: 已创建, **README.md**: 已创建, **封装脚本**: 已创建 (`scripts/browser.sh`), **agent-browser**: 已安装 (v0.13.0), **功能测试**: 全部通过

---

## 安装详情
- **工具名称**: agent-browser, **版本**: 0.13.0, **安装方式**: npm 全局安装, **安装路径**: `/usr/bin/agent-browser`
- **类型**: Rust CLI + Node.js 回退

## 功能验证

### 已测试并验证的功能
help 命令, 状态=, 备注=显示完整命令列表
snapshot, 状态=, 备注=返回可访问性树 (AI 友好)
get title, 状态=, 备注=获取页面标题
get url, 状态=, 备注=获取当前 URL
wait --load networkidle, 状态=, 备注=等待网络空闲
find role heading text, 状态=, 备注=语义定位工作正常
screenshot, 状态=, 备注=生成 158KB 截图
JavaScript eval, 状态=, 备注=执行 JS 正常
close, 状态=, 备注=关闭浏览器

### 测试用例
```bash

# 1. 打开网页
agent-browser open https://httpbin.org/html

# 2. 获取快照
agent-browser snapshot

# 3. 截图
agent-browser screenshot /tmp/test-browser.png

# 4. 关闭浏览器
agent-browser close

# 关闭成功
```

## 与现有工具对比
**agent-browser**, 优势=高性能,零依赖,语义定位, 劣势=需要下载 Chromium, 适用场景=需要交互,执行 JS
**jina-reader**, 优势=纯 API,无需浏览器, 劣势=不能交互,无法执行 JS, 适用场景=静态内容抓取
**web_fetch**, 优势=内置,快速, 劣势=功能有限, 适用场景=简单页面获取
**browser**, 优势=功能强大, 劣势=依赖 Chrome 扩展, 适用场景=复杂自动化任务

## 使用建议

### 优先使用 agent-browser 的场景
1. 需要与页面交互(点击,填充表单)
2. 需要执行 JavaScript
3. 需要截图或 PDF
4. 需要等待页面动态加载
5. 需要语义定位 (ARIA role)

### 使用 jina-reader 的场景
1. 只需要纯文本内容
2. Twitter/X 帖子抓取
3. PDF/文档提取
4. 追求速度(无浏览器开销)

## 文档结构
/root/.openclaw/workspace/skills/agent-browser/
├── SKILL.md # 完整使用指南
├── README.md # 快速参考
├── scripts/
│ ├── browser.sh # 命令封装脚本
│ └── test.sh # 功能测试脚本
└── INSTALL_REPORT.md # 本文件

## 下一步

### 立即可用
- 使用 `agent-browser open <url>` 自动化浏览器操作
- 使用 `agent-browser snapshot` 获取 AI 友好的页面结构
- 使用 `agent-browser screenshot` 截图

### 可选优化
- [ ] 下载 Chromium(首次使用时自动下载)
- [ ] 创建工作流模板(如登录,数据抓取), [ ] 集成到现有自动化脚本, [ ] 创建高级示例(如爬虫,表单填充)

## 使用示例

### 示例 1:搜索并截图
agent-browser open https://www.google.com
agent-browser find role textbox fill --name "Search" "OpenClaw AI"
agent-browser find role button click --name "Google Search"
agent-browser wait --load networkidle
agent-browser screenshot /tmp/search.png

### 示例 2:数据抓取
agent-browser open https://example.com/products
agent-browser eval "
 const titles = document.querySelectorAll('h1, h2, h3');
 return Array.from(titles).map(el => el.textContent);
" > products.txt

### 示例 3:表单自动化
agent-browser open https://httpbin.org/forms/post
agent-browser fill "#custname" "Test User"
agent-browser fill "#custtel" "1234567890"
agent-browser fill "#custemail" "test@example.com"
agent-browser click "#submit"
agent-browser screenshot /tmp/form-result.png

## 资源
- **官方文档**: https://github.com/vercel-labs/agent-browser
- **本地文档**: `SKILL.md` / `README.md`
- **命令参考**: `agent-browser --help`

**报告生成时间**: 2026-02-22 20:10:26
**工具版本**: agent-browser v0.13.0
**状态**: 安装完成且功能正常