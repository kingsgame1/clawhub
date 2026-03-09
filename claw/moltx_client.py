"""
Moltx API Client - Moltx API 集成（ClawWork 适配）
获取 Moltx Article 互动数据，用于质量评估
"""

import json
import logging
import requests
from typing import Dict, Optional, List
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MoltxClient:
    """
    Moltx API 客户端
        
    功能：
    - 获取 Article 信息
    - 获取 Article 互动数据（likes, comments）
    - 获取 Agent 信息
    """

    def __init__(self, api_key: str, base_url: str = "https://api.moltx.xyz"):
        """
        初始化客户端
        
        Args:
            api_key: Moltx API Key（用于 Moltx API 调用）
            base_url: API 基础 URL
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def get_article(self, article_id: str) -> Optional[Dict]:
        """
        获取 Article 信息
        
        Args:
            article_id: Article ID
            
        Returns:
            Article 信息或 None
        """
        try:
            # Moltx API 端点（根据实际 API 规范调整）
            url = f"{self.base_url}/v1/articles/{article_id}"
            
            response = requests.get(
                url,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ 获取到 Article: {article_id}")
                return data
            else:
                logger.warning(f"⚠️  Article 请求失败: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 获取 Article 错误: {e}")
            return None

    def get_article_interactions(self, article_id: str) -> Dict[str, any]:
        """
        获取 Article 互动数据
        
        Args:
            article_id: Article ID
            
        Returns:
            互动数据 {"likes": int, "comments": List[Dict], "shares": int}
        """
        try:
            # 直接从 Article 数据中提取互动信息
            article_data = self.get_article(article_id)
            
            if not article_data:
                return {
                    "likes": 0,
                    "comments": [],
                    "shares": 0,
                    "article_id": article_id
                }

            # 提取互动数据（根据实际 API 响应结构调整）
            interactions = {
                "likes": article_data.get("likes_count", 0),
                "comments": article_data.get("comments", []) or [],
                "shares": article_data.get("shares_count", 0),
                "article_id": article_id,
                "views": article_data.get("views_count", 0)
            }

            logger.info(f"📊 Article {article_id} 互动数据:")
            logger.info(f"   Likes: {interactions['likes']}")
            logger.info(f"   Comments: {len(interactions['comments'])}")
            logger.info(f"   Shares: {interactions['shares']}")
            
            return interactions

        except Exception as e:
            logger.error(f"❌ 获取互动数据错误: {e}")
            return {
                "likes": 0,
                "comments": [],
                "shares": 0,
                "article_id": article_id
            }

    def get_my_articles(
        self,
        agent_id: str,
        date: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict]:
        """
        获取我的 Articles 列表
        
        Args:
            agent_id: Agent ID
            date: 日期（YYYY-MM-DD），默认为今天
            limit: 返回数量限制
            
        Returns:
            Articles 列表
        """
        try:
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")

            # Moltx API 端点（根据实际 API 规范调整）
            url = f"{self.base_url}/v1/agents/{agent_id}/articles"
            
            params = {
                "date": date,
                "limit": limit
            }
            
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get("articles", [])
                logger.info(f"✅ 获取到 {len(articles)} 篇 Article（{date}）")
                return articles
            else:
                logger.warning(f"⚠️  Articles 列表请求失败: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"❌ 获取 Articles 列表错误: {e}")
            return []

    def get_agent_info(self, agent_id: str) -> Optional[Dict]:
        """
        获取 Agent 信息
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent 信息或 None
        """
        try:
            url = f"{self.base_url}/v1/agents/{agent_id}"
            
            response = requests.get(
                url,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ 获取到 Agent 信息: {agent_id}")
                return data
            else:
                logger.warning(f"⚠️  Agent 请求失败: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"❌ 获取 Agent 信息错误: {e}")
            return None


class MoltxMockClient:
    """
    Moltx Mock 客户端（用于测试和 API 不可用时）
    返回模拟数据，使系统可以继续运行
    """

    def __init__(self):
        # 模拟数据存储
        self.mock_articles = {}

    def register_mock_article(
        self,
        article_id: str,
        mock_data: Dict = None
    ) -> None:
        """
        注册模拟 Article
        
        Args:
            article_id: Article ID
            mock_data: 模拟数据（默认随机生成）
        """
        if mock_data is None:
            import random
            mock_data = {
                "likes_count": random.randint(5, 20),
                "shares_count": random.randint(1, 5),
                "views_count": random.randint(50, 200),
                "comments": [
                    {"agent_id": "mock1", "content": "Nice!"},
                    {"agent_id": "mock2", "content": "Good point!"}
                ]
            }
        
        self.mock_articles[article_id] = mock_data
        logger.info(f"📝 注册模拟 Article: {article_id}")

    def get_article_interactions(self, article_id: str) -> Dict[str, any]:
        """
        获取模拟互动数据
        
        Args:
            article_id: Article ID
            
        Returns:
            模拟互动数据
        """
        if article_id in self.mock_articles:
            data = self.mock_articles[article_id]
            return {
                "likes": data.get("likes_count", 0),
                "comments": data.get("comments", []),
                "shares": data.get("shares_count", 0),
                "article_id": article_id,
                "mock": True
            }
        else:
            # 返回默认模拟数据
            return {
                "likes": 5,
                "comments": [{"agent_id": "mock", "content": "Mock"}],
                "shares": 1,
                "article_id": article_id,
                "mock": True
            }


# 全局客户端实例（根据配置初始化）
_moltx_client = None
_moltx_mock_client = MoltxMockClient()


def init_moltx_client(api_key: Optional[str] = None, use_mock: bool = False) -> None:
    """
    初始化 Moltx 客户端
    
    Args:
        api_key: API Key
        use_mock: 是否使用 Mock 客户端
    """
    global _moltx_client, _moltx_mock_client
    
    if use_mock:
        logger.info("🧪 使用 Moltx Mock 客户端")
        _moltx_client = _moltx_mock_client
    else:
        if not api_key:
            logger.warning("⚠️  未提供 API Key，使用 Mock 客户端")
            _moltx_client = _moltx_mock_client
        else:
            _moltx_client = MoltxClient(api_key)


def get_moltx_client() -> MoltxClient:
    """获取全局 Moltx 客户端"""
    return _moltx_client


# 便捷函数
def get_article_interactions(article_id: str) -> Dict[str, any]:
    """获取 Article 互动数据（便捷函数）"""
    client = get_moltx_client()
    return client.get_article_interactions(article_id)


if __name__ == "__main__":
    # 测试代码
    print("\n🧪 测试 Moltx Mock 客户端...")
    
    # 初始化 Mock 客户端
    init_moltx_client(use_mock=True)
    
    # 注册模拟数据
    mock_client = get_moltx_client()
    mock_client.register_mock_article("test-001", {
        "likes_count": 12,
        "shares_count": 3,
        "comments": [
            {"agent_id": "agent1", "content": "Great article!"},
            {"agent_id": "agent2", "content": "Insightful!"},
            {"agent_id": "agent3", "content": "Good read!"}
        ]
    })
    
    # 获取互动数据
    interactions = get_article_interactions("test-001")
    print(f"   互动数据: {json.dumps(interactions, indent=2)}")

    # 测试不存在的 Article
    interactions = get_article_interactions("unknown-001")
    print(f"   未知 Article 数据: {json.dumps(interactions, indent=2)}")
