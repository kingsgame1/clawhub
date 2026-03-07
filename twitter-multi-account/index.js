#!/usr/bin/env node

/**
 * 多账户 Twitter/X 批量管理系统 - 主入口
 * 集成 SkillPay 支付系统
 */

const { exec } = require('child_process');
const path = require('path');
const { checkAndCharge } = require('./skillpay_integration');

// 支持 OpenClaw 调用格式: node index.js --action xxx --param yyy
const args = process.argv.slice(2);
const action = args.find(arg => arg.startsWith('--action='))?.split('=')[1] || 'help';

async function main() {
  console.log('🐦 多账户 Twitter/X 批量管理系统 v1.0.0');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

  // 第1步: 检查余额并扣费 (每次调用 1 token)
  console.log('🔒 支付验证中...');
  const paymentResult = await checkAndCharge(1);

  if (!paymentResult.success) {
    console.error('\n❌ 支付失败，无法继续执行');
    console.error(`💳 充值链接: ${paymentResult.paymentLink}`);
    process.exit(1);
  }

  console.log('✅ 支付验证通过，开始执行...\n');

  // 第2步: 路由到对应的Python脚本
  const scriptsDir = path.join(__dirname, 'scripts');

  try {
    let script, scriptArgs;

    switch (action) {
      case 'add-account':
        script = path.join(scriptsDir, 'add_account.py');
        scriptArgs = args.filter(arg => !arg.startsWith('--action='));
        break;

      case 'list-accounts':
        script = path.join(scriptsDir, 'list_accounts.py');
        scriptArgs = args.filter(arg => !arg.startsWith('--action='));
        break;

      case 'post':
        script = path.join(scriptsDir, 'post.py');
        scriptArgs = args.filter(arg => !arg.startsWith('--action='));
        break;

      case 'help':
        showHelp();
        process.exit(0);

      default:
        console.error(`❌ 未知操作: ${action}`);
        showHelp();
        process.exit(1);
    }

    // 执行Python脚本
    await executeScript(script, scriptArgs);

  } catch (error) {
    console.error(`\n❌ 执行失败: ${error.message}`);
    process.exit(1);
  }
}

function executeScript(script, scriptArgs) {
  return new Promise((resolve, reject) => {
    const cmd = `python3 ${script} ${scriptArgs.join(' ')}`;
    console.log(`📝 执行: ${cmd}\n`);

    const child = exec(cmd, { cwd: __dirname }, (error, stdout, stderr) => {
      if (error) {
        console.error(stderr);
        reject(error);
      } else {
        console.log(stdout);
        resolve();
      }
    });

    // 实时输出
    child.stdout?.pipe(process.stdout);
    child.stderr?.pipe(process.stderr);
  });
}

function showHelp() {
  console.log(`
📖 使用方法:

  node index.js --action=add-account [--username USER] [--password PASS] [--type api|auto]
    添加 Twitter 账户

  node index.js --action=list-accounts
    列出所有账户

  node index.js --action=post [--account @user] [--text "内容"] [--media PATH] [--schedule TIME]
    发布推文

💰 每次调用消耗 1 token (0.001 USDT)

⚙️  环境变量:
  SKILL_BILLING_API_KEY - SkillPay API密钥
  SKILL_ID - Skill ID（发布后从ClawHub获取）
  TWITTER_AUTO_MODE - 浏览器自动化模式（推荐）
  TWITTER_API_KEY - Twitter API 密钥（可选）

📚 文档: 查看 SKILL.md 了解详细使用指南
  `);
}

// 只有直接运行时才执行，require时不执行
if (require.main === module) {
  main().catch(error => {
    console.error('\n💥 致命错误:', error);
    process.exit(1);
  });
}

module.exports = { main };
