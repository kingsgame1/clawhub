# CoinGecko API 参考

## 免费定价端点

### 获取当前价格
```bash
GET https://api.coingecko.com/api/v3/simple/price
参数:
 - ids: bitcoin,ethereum,... (逗号分隔), vs_currencies: usd,eur,cny,... (逗号分隔), include_market_cap: true/false, include_24hr_change: true/false
```

**示例**:

curl "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true"

**响应**:

```json
{
 "bitcoin": {
 "usd": 71423,
 "usd_24h_change": 2.34
 },
 "ethereum": {
 "usd": 3850,
 "usd_24h_change": -1.23
 }

## 限制
- 免费端点:10-50 次/分钟
- VIP 端点:需要 API Key($79/月起)

## 最佳实践
1. **缓存价格**:2-5 秒,避免重复请求
2. **批量查询**:一次获取多个币种价格
3. **错误处理**:429 响应时等待 60 秒重试

## 替代方案
如果遇到限流:
- Binance API(免费,基础行情), CryptoCompare(免费额度较高), 自建服务器缓存(Redis)