#!/usr/bin/env node

/**
 * Price Alerts — 智能价格波动警报系统
 * 集成 SkillPay 支付系统
 */

require('dotenv').config();
const { handleRequest } = require('./skillpay_integration');

// 解析命令行参数
const args = process.argv.slice(2);
const params = {};

for (let i = 0; i < args.length; i++) {
  if (args[i].startsWith('--')) {
    const arg = args[i].slice(2);
    if (arg.includes('=')) {
      // 支持格式 --key=value
      const [key, value] = arg.split('=', 2);
      params[key] = value;
    } else {
      // 支持格式 --key value 或 --key
      const key = arg;
      const value = args[i + 1];
      if (value && !value.startsWith('--')) {
        params[key] = value;
        i++;
      } else {
        params[key] = true;
      }
    }
  }
}

/**
 * 价格监控主逻辑
 */
async function runPriceAlerts(options) {
  const { action, symbol, threshold, type } = options;

  console.log(`🚀 Price Alerts 执行中...`);
  console.log(`- 标的: ${symbol}`);
  console.log(`- 类型: ${type || 'price_above'}`);
  console.log(`- 阈值: ${threshold}`);

  // 这里调用 Python 脚本执行实际的价格监控逻辑
  const { spawn } = require('child_process');

  return new Promise((resolve, reject) => {
    let command;

    if (action === 'init') {
      command = spawn('python3', ['scripts/init_config.py', `--market`, 'crypto', `--symbol`, symbol], {
        cwd: __dirname
      });
    } else if (action === 'monitor') {
      command = spawn('python3', ['scripts/start_monitor.py', `--symbol`, symbol], {
        cwd: __dirname
      });
    } else {
      reject(new Error(`Unknown action: ${action}`));
      return;
    }

    command.stdout.on('data', (data) => {
      console.log(data.toString().trim());
    });

    command.stderr.on('data', (data) => {
      console.error(data.toString().trim());
    });

    command.on('close', (code) => {
      if (code === 0) {
        resolve({ message: '✅ 执行成功' });
      } else {
        reject(new Error(`执行失败，退出码: ${code}`));
      }
    });
  });
}

/**
 * 主入口：支付验证 + 执行
 */
async function main() {
  const userId = params.userId || 'default-user';
  const action = params.action || 'monitor';

  console.log(`🔍 用户 ID: ${userId}`);
  console.log(`🔧 操作: ${action}`);

  try {
    // 使用 SkillPay 验证支付并执行技能
    const result = await handleRequest(userId, async () => {
      return await runPriceAlerts(params);
    });

    if (result.success) {
      console.log(`\n✅ 技能执行成功！`);
      console.log(`当前余额: ${result.balance} tokens`);
    } else {
      console.log(`\n❌ 余额不足，请充值`);
      console.log(`充值链接: ${result.paymentUrl}`);
      console.log(`当前余额: ${result.balance} tokens`);
      process.exit(1);
    }
  } catch (error) {
    console.error(`\n❌ 执行失败:`, error.message);
    process.exit(1);
  }
}

// 直接调用 Python 脚本（跳过支付验证，用于测试）
if (params.skipPayment) {
  console.log('⚠️ 跳过支付验证，直接执行（仅用于测试）');
  runPriceAlerts(params)
    .then(() => console.log('\n✅ 执行完成'))
    .catch(err => console.error('\n❌ 失败:', err.message));
} else {
  main();
}
