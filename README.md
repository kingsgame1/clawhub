# OpenClaw Skills Collection

我的 OpenClaw Agent 技能集合

## 📦 已发布到 ClawHub 的 Skills

### 🤖 BotLearn Post Strategy Analyzer
**Slug**: `botlearn-post-strategy`  
**Version**: 1.0.0  
**目录**: `botlearn-post-strategy/`

BotLearn 社区自动化发帖策略分析器，支持：
- 帖子表现分析
- 互动率预测
- 最佳发牌时间推荐
- SkillPay 集成 (0.001 USDT/次)

### 💰 Price Alerts System
**Slug**: `price-alerts`  
**Version**: 1.0.0  
**目录**: `price-alerts/`

智能价格波动警报系统，支持：
- 加密货币/股票/外汇多市场监控
- 自定义警报规则
- 多渠道通知
- 历史回测

### 🐦 Twitter Multi-Account
**Slug**: `twitter-multi-account`  
**Version**: 1.0.0  
**目录**: `twitter-multi-account/`

Twitter/X 多账户批量管理系统，支持：
- 并发发帖
- 日程安排
- 互动追踪
- 数据分析

## 🔧 安装

使用 ClawHub CLI 安装：

```bash
npx clawhub install botlearn-post-strategy
npx clawhub install price-alerts
npx clawhub install twitter-multi-account
```

## 📝 开发说明

每个 skill 都是独立的功能模块，可单独使用或组合使用。

### 目录结构

```
skills/
├── botlearn-post-strategy/      # BotLearn 发牌策略
├── price-alerts/                 # 价格警报系统
├── twitter-multi-account/        # Twitter 多账户管理
└── ...                           # 其他开发中的 skills
```

## 🤝 贡献

欢迎 Pull Request！

## 📄 许可证

MIT License
