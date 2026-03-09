# Agent Swarm - 简易版
多 Agent 协作系统,支持并行任务执行,进度监控,失败重试.

## 架构
```
Orchestrator (主 Agent)
 ↓
┌─────┴─────┬────────┬────────┐
↓ ↓ ↓ ↓
Agent-1 Agent-2 Agent-3 Agent-4
(独立会话) (独立会话) (独立会话) (独立会话)

## 使用方法

### 1. 创建任务
在 `tasks/` 目录下创建任务文件:

```markdown

# tasks/2026-02-24-fix-api-bug.md
任务类型: bugfix
优先级: high
超时: 30分钟

描述:
修复 API 接口 /api/users 的 500 错误

前置条件:
- 读取错误日志 logs/api-errors.log
- 查看 backend/src/api/users.ts

验收标准:
- API 返回 200 状态码
- 单元测试通过

### 2. 启动 Agent Swarm
启动 agent-swarm 任务: [任务路径或任务描述]

### 3. 监控状态
查看 agent-swarm 状态

### 4. 手动干预
重试 agent [agent_id]
停止 agent [agent_id]
发送消息到 agent [agent_id]: "<消息>"

## 配置
- `scripts/agent-swarm/config.json` - 全局配置
- `scripts/agent-swarm/registry.json` - 任务注册表(运行时生成)

## 核心功能
- 并行任务执行:, 进度跟踪:, 失败重试:, Telegram 通知:, 手动干预:, 任务优先级:, 预估时间: ️ 基础版

## 示例场景
1. **Bug 修复**: 3 个 agent 并行修复不同 bug
2. **功能开发**: agent-1 写后端,agent-2 写前端,agent-3 写测试
3. **文档更新**: 多个 agent 并行更新不同模块文档
4. **日志分析**: 扫描日志文件,生成报告