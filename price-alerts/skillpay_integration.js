/**
 * SkillPay Billing SDK — Node.js
 *
 * [EN] 1 USDT = 1000 tokens | 1 call = 1 token | Min deposit 8 USDT
 * [中文] 1 USDT = 1000 tokens | 每次 1 token | 最低充值 8 USDT
 *
 * Endpoints:
 *   POST /billing/charge       — 扣费
 *   GET  /billing/balance      — 余额查询
 *   POST /billing/payment-link — 充值链接
 */

const axios = require('axios');

const BILLING_URL = 'https://skillpay.me/api/v1/billing';
const API_KEY = process.env.SKILL_BILLING_API_KEY;
const SKILL_ID = process.env.SKILL_ID;

const headers = { 'X-API-Key': API_KEY, 'Content-Type': 'application/json' };

if (!API_KEY || !SKILL_ID) {
  console.error('❌ SkillPay 配置缺失: 需要设置 SKILL_BILLING_API_KEY 和 SKILL_ID 环境变量');
  process.exit(1);
}

/**
 * 扣费 (每次 1 token)
 * @param {string} userId 用户 ID
 * @returns {Promise<Object>} { ok: boolean, balance: number, payment_url?: string }
 */
async function chargeUser(userId) {
  try {
    const { data } = await axios.post(BILLING_URL + '/charge', {
      user_id: userId,
      skill_id: SKILL_ID,
      amount: 0, // 每次调用固定 1 token
    }, { headers });

    if (data.success) {
      return { ok: true, balance: data.balance };
    }
    return { ok: false, balance: data.balance, payment_url: data.payment_url };
  } catch (error) {
    console.error('❌ 扣费失败:', error.response?.data || error.message);
    throw error;
  }
}

/**
 * 查询余额
 * @param {string} userId 用户 ID
 * @returns {Promise<number>} 余额（tokens）
 */
async function getBalance(userId) {
  try {
    const { data } = await axios.get(BILLING_URL + '/balance', {
      params: { user_id: userId },
      headers,
    });
    return data.balance;
  } catch (error) {
    console.error('❌ 查询余额失败:', error.response?.data || error.message);
    throw error;
  }
}

/**
 * 生成充值链接
 * @param {string} userId 用户 ID
 * @param {number} amount 充值金额（USDT）
 * @returns {Promise<string>} 支付链接
 */
async function getPaymentLink(userId, amount = 8) {
  try {
    const { data } = await axios.post(BILLING_URL + '/payment-link', {
      user_id: userId,
      amount,
    }, { headers });
    return data.payment_url;
  } catch (error) {
    console.error('❌ 生成充值链接失败:', error.response?.data || error.message);
    throw error;
  }
}

/**
 * 主处理函数：验证支付并执行技能
 * @param {string} userId 用户 ID
 * @param {Function} skillFunction 执行技能的函数
 * @returns {Promise<Object>} 执行结果
 */
async function handleRequest(userId, skillFunction) {
  const charge = await chargeUser(userId);

  if (charge.ok) {
    // ✅ 余额充足，执行技能
    const result = await skillFunction();
    return { success: true, result, balance: charge.balance };
  } else {
    // ❌ 余额不足，返回充值链接
    return {
      success: false,
      paymentUrl: charge.payment_url,
      balance: charge.balance,
      message: '余额不足，请充值后重试'
    };
  }
}

module.exports = {
  chargeUser,
  getBalance,
  getPaymentLink,
  handleRequest
};
