---
name: twitter-multi-account
description: 多账户 Twitter/X 批量管理系统,支持并发发帖,日程安排,互动追踪,数据分析.使用场景:(1) 管理多个 Twitter 账号(品牌矩阵,个人+工作号),(2) 批量定时发帖(不同账号发不同内容),(3) 追踪所有账号的互动(评论,转发,喜欢),(4) 生成跨账号数据报告.支持浏览器自动化(Playwright)或 API 方式.

# Twitter/X 多账户批量管理

## 快速开始

### 配置账户
```bash

# 添加第一个账户
scripts/add_account.py --name work --session-file sessions/work.json

# 添加第二个账户
scripts/add_account.py --name brand --session-file sessions/brand.json
```

### 查看账户列表
scripts/list_accounts.py

### 单账号发帖
scripts/post.py --account work --content "Hello, world!"

### 批量发帖(所有账号)
scripts/batch_post.py --content "公告内容" --schedule "2026-03-07 10:00"

## 核心功能

### 1. 账户管理
支持的账户配置方式:

**Cookie + Session**, 适用场景=个人账号, 优缺点=无 API 限制,但需频繁登录
**Twitter API v2**, 适用场景=商业账号, 优缺点=官方支持,但有限额
**浏览器自动化**, 适用场景=临时项目, 优缺点=模拟真人行为,但慢

### 2. 发帖功能

#### 即时发帖
scripts/post.py \
 --account work \
 --content "这是我的第一个帖子" \
 --images assets/image1.png,assets/image2.png \
 --hashtags tech,ai,automation

#### 定时发帖
--account brand \
 --content "产品发布公告" \
 --schedule "2026-03-07 14:00:00" \
 --timezone America/New_York

#### 批量发帖策略
**策略 A: 同一内容,不同账号**
scripts/batch_post.py \
 --accounts work,brand,personal \
 --content "重要公告" \
 --delay 300 # 每个账号间隔 5 分钟

**策略 B: 不同内容,不同账号**

# 创建批量配置文件
cat > batch_config.json << 'EOF'
{
 "posts": [
 {"account": "work", "content": "工作账号内容"},
 {"account": "brand", "content": "品牌账号内容"},
 {"account": "personal", "content": "个人账号内容"}
 ],
 "schedule": "2026-03-07 10:00",
 "delay": 300
}
EOF

scripts/batch_post.py --config batch_config.json

# 追踪所有账号的最新互动
scripts/track_interactions.py --hours 24

# 生成互动报告
scripts/generate_report.py --output reports/monthly.html

支持追踪的互动类型:
- 新评论(实时通知), 转发统计, 点赞数增长, 粉丝变化

# 跨账号数据汇总
scripts/analyze_accounts.py --days 30

# 对比账号表现
scripts/compare_accounts.py --account1 work --account2 brand

输出指标:
- 发帖频率, 平均互动率, 最佳发帖时间, 内容表现排名, 粉丝增长率

## 日程管理

# 添加日程项
scripts/schedule_add.py \
 --content "周一晨会预告" \
 --time "2026-03-07 09:00" \
 --repeat weekly

# 查看日程
scripts/schedule_list.py --account work

# 检查待执行的日程
scripts/schedule_check.py

# 执行所有到期日程
scripts/schedule_run.py

建议使用 cron 自动化:

*/15 * * * * /path/to/skills/twitter-multi-account/scripts/schedule_run.py

## 高级功能

# 使用模板发帖
--template templates/announcement.md \
 --data '{"product": "新功能", "date": "2026-03-07"}'

模板示例:

```markdown

# {{product}} 发布预告
我们将于 {{date}} 发布全新的 {{product}}.

敬请期待!#新功能 #产品发布

# 创建 A/B 测试
scripts/ab_test.py \
 --accounts work,brand \
 --content-a "标题 A" \
 --content-b "标题 B" \
 --schedule "2026-03-07 10:00"

系统会跟踪两个内容的互动数据,自动报告效果.

# 添加监控对象
scripts/competitor_add.py --handle @competitor

# 查看竞品动态
scripts/competitor_watch.py

## 安全与反检测

### 避免限制的最佳实践
1. **时间间隔**:同一账号发帖间隔 ≥ 30 分钟
2. **内容差异化**:避免重复内容
3. **IP 轮换**:使用代理(如果大量操作)
4. **模拟真人**:随机化发帖时间 ±10 分钟
5. **渐进式增长**:新账号首日 ≤ 5 条

### 检测警报
scripts/check_ratelimit.py --account work

检测项目:
- Rate Limit 状态, 账号状态(是否受限), 异常活动检测

# 导出为 CSV
scripts/export.py --format csv --output exports/posts.csv

# 导出为 JSON
scripts/export.py --format json --output exports/data.json

# 导出交互式报告(HTML)
scripts/export.py --format html --output reports/overview.html

## 错误处理

### 常见错误
Rate Limit, 原因=操作太快, 解决方案=等待 15 分钟后重试
Session Expired, 原因=Cookie 失效, 解决方案=重新登录更新 session
403 Forbidden, 原因=IP 被限制, 解决方案=切换代理或等待
429 Too Many Requests, 原因=发帖过频, 解决方案=增加间隔时间

### 重试机制
内置自动重试(线性退避):

# 自定义重试参数
--content "测试" \
 --max-retries 3 \
 --retry-delay 60

## 参考文档
- Twitter API v2 文档: `references/twitter_api_v2.md`
- 浏览器自动化参考: `references/playwright_guide.md`
- 反检测策略: `references/anti_detection.md`

## 配置文件结构
twitter-multi-account/
├── accounts.json # 账户配置
├── schedule.json # 日程表
├── sessions/ # Session 文件目录
├── assets/ # 图片,视频资源
├── templates/ # 内容模板
├── reports/ # 数据报告
└── exports/ # 导出文件

## SkillPay 支付集成
本技能已集成 SkillPay 支付系统,按次付费使用.

### 费用说明
- 每次调用消耗 **1 token** (0.001 USDT)
- 1 USDT = 1000 tokens
- 扣费成功后才执行技能功能
- 余额不足时会返回充值链接

### 环境变量配置
创建 `.env` 文件(参考 `.env.example`):

# 必需:SkillPay 配置
SKILL_BILLING_API_KEY=your_skillpay_api_key_here
SKILL_ID=your_skill_id_here

# 方式1: 浏览器自动化(推荐,无需 API Key)
TWITTER_AUTO_MODE=true

# 方式2: 官方 API
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret
TWITTER_BEARER_TOKEN=your_bearer_token

### Node.js 入口
使用集成的 Node.js 入口(推荐,支持自动扣费):

# 安装依赖
npm install

# 添加账户(自动扣费)
node index.js --action=add-account --name work

# 列出账户
node index.js --action=list-accounts

# 发布推文
node index.js --action=post --account work --text "Hello, world!"

### 直接使用 Python 脚本(无需扣费)
如果你想跳过支付验证,可以直接运行Python脚本:

python3 scripts/add_account.py --name work
python3 scripts/post.py --account work --content "Hello, world!"

️ **注意**: 直接使用Python脚本不会进行支付验证,仅用于本地调试或测试.

## 发布检查清单
在发布到 ClawHub 前,请确认以下项目:

- [ ] 已设置环境变量 `SKILL_BILLING_API_KEY` 和 `SKILL_ID`
- [ ] 已运行 `npm install` 安装依赖
- [ ] 已测试 `node index.js --action=list-accounts` 确认支付流程正常
- [ ] SKILL.md 已更新支付说明
- [ ] `.env.example` 包含所有必要的环境变量
- [ ] Python 脚本有执行权限 (`chmod +x scripts/*.py`)

发布后从 ClawHub 获取Skill ID,更新 `.env` 文件中的 `SKILL_ID`.

*版本: 1.0.0 | 更新日期: 2026-03-07 | 集成 SkillPay 支付*