/**
 * SkillPay 支付集成模块
 * 提供余额查询、扣费、充值链接生成功能
 */

const axios = require('axios');

const SKILLPAY_BASE_URL = 'https://api.skillpay.io';
const API_KEY = process.env.SKILL_BILLING_API_KEY;
const SKILL_ID = process.env.SKILL_ID;

if (!API_KEY || !SKILL_ID) {
  console.error('❌ SkillPay 配置缺失: 需要设置 SKILL_BILLING_API_KEY 和 SKILL_ID 环境变量');
  process.exit(1);
}

/**
 * 查询余额
 * @returns {Promise<number>} 余额（tokens）
 */
async function getBalance() {
  try {
    const response = await axios.get(`${SKILLPAY_BASE_URL}/billing/balance`, {
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json'
      }
    });
    return response.data.balance || 0;
  } catch (error) {
    console.error('❌ 查询余额失败:', error.response?.data || error.message);
    throw error;
  }
}

/**
 * 扣费（1 token = 0.001 USDT）
 * @param {number} tokens 要扣除的token数量（默认1）
 * @returns {Promise<boolean>} 是否扣费成功
 */
async function charge(tokens = 1) {
  try {
    const response = await axios.post(`${SKILLPAY_BASE_URL}/billing/charge`, {
      skill_id: SKILL_ID,
      tokens: tokens,
      description: `${SKILL_ID} - Skill调用 (${tokens} tokens)`
    }, {
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json'
      }
    });

    if (response.data.success) {
      console.log(`✅ 扣费成功: ${tokens} tokens (剩余: ${response.data.balance || '未知'})`);
      return true;
    } else {
      console.error('❌ 扣费失败:', response.data.message || '未知错误');
      return false;
    }
  } catch (error) {
    if (error.response?.status === 402) {
      // 余额不足
      console.error('❌ 余额不足，请先充值');
      return false;
    }
    console.error('❌ 扣费失败:', error.response?.data || error.message);
    throw error;
  }
}

/**
 * 生成充值链接
 * @returns {Promise<string>} 充值链接
 */
async function generatePaymentLink() {
  try {
    const response = await axios.post(`${SKILLPAY_BASE_URL}/billing/payment-link`, {
      skill_id: SKILL_ID
    }, {
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json'
      }
    });

    return response.data.payment_link || response.data.url;
  } catch (error) {
    console.error('❌ 生成充值链接失败:', error.response?.data || error.message);
    throw error;
  }
}

/**
 * 检查余额并扣费，余额不足时返回充值链接
 * @param {number} tokens 要扣除的token数量
 * @returns {Promise<{success: boolean, balance?: number, paymentLink?: string}>}
 */
async function checkAndCharge(tokens = 1) {
  const balance = await getBalance();
  console.log(`💰 当前余额: ${balance} tokens`);

  if (balance < tokens) {
    console.error(`⚠️ 余额不足 (需要 ${tokens} tokens, 当前 ${balance} tokens)`);
    const paymentLink = await generatePaymentLink();
    return {
      success: false,
      balance: balance,
      paymentLink: paymentLink
    };
  }

  const charged = await charge(tokens);
  if (!charged) {
    const paymentLink = await generatePaymentLink();
    return {
      success: false,
      balance: balance,
      paymentLink: paymentLink
    };
  }

  return {
    success: true,
    balance: balance - tokens
  };
}

module.exports = {
  getBalance,
  charge,
  generatePaymentLink,
  checkAndCharge
};
