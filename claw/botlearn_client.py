"""
BotLearn API Client - BotLearn API 集成（ClawWork 适配）
获取 BotLearn 社区互动数据，用于质量评估
"""

import json
import logging
import requests
from typing import Dict, Optional, List
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BotLearnClient:
    """
    BotLearn API 客户端
        
    功能：
    - 获取 Post 信息
    - 获取 Post 互动数据（likes, comments）
    - 获取社区活动统计
    """

    def __init__(self, api_key: str, base_url: str = "https://botlearn.ai/api"):
        """
        初始化客户端
        
        Args:
            api_key: BotLearn API Key
            base_url: API 基础 URL
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def get_post(self, post_id: str) -> Optional[Dict]:
        """
        获取 Post 信息
        
        Args:
            post_id: Post ID
            
        Returns:
            Post 信息或 None
        """
        try:
            # BotLearn API 端点（根据实际 API 规范调整）
            url = f"{self.base_url}/community/posts/{post_id}"
            
            response = requests.get(
                url,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ 获取到 Post: {post_id}")
                return data
            else:
                logger.warning(f"⚠️  Post 请求失败: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 获取 Post 错误: {e}")
            return None

    def get_post_interactions(self, post_id: str) -> Dict[str, any]:
        """
        获取 Post 互动数据
        
        Args:
            post_id: Post ID
            
        Returns:
            互动数据 {"likes_received": int, "replies": int, "content_length": int}
        """
        try:
            # 直接从 Post 数据中提取互动信息
            post_data = self.get_post(post_id)
            
            if not post_data:
                return {
                    "likes_received": 0,
                    "replies": 0,
                    "content_length": 0,
                    "post_id": post_id
                }

            # 提取互动数据（根据实际 API 响应结构调整）
            interactions = {
                "likes_received": post_data.get("score", 0),
                "replies": post_data.get("commentCount", 0),
                "content_length": len(post_data.get("content", "")),
                "post_id": post_id,
                "view_count": post_data.get("viewCount", 0)
            }

            logger.info(f"📊 Post {post_id} 互动数据:")
            logger.info(f"   Likes: {interactions['likes_received']}")
            logger.info(f"   Replies: {interactions['replies']}")
            logger.info(f"   Content: {interactions['content_length']} 字符")
            
            return interactions

        except Exception as e:
            logger.error(f"❌ 获取互动数据错误: {e}")
            return {
                "likes_received": 0,
                "replies": 0,
                "content_length": 0,
                "post_id": post_id
            }

    def get_comment(self, comment_id: str) -> Optional[Dict]:
        """
        获取 Comment 信息
        
        Args:
            comment_id: Comment ID
            
        Returns:
            Comment 信息或 None
        """
        try:
            url = f"{self.base_url}/community/comments/{comment_id}"
            
            response = requests.get(
                url,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ 获取到 Comment: {comment_id}")
                return data
            else:
                logger.warning(f"⚠️  Comment 请求失败: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"❌ 获取 Comment 错误: {e}")
            return None

    def get_comment_interactions(self, comment_id: str) -> Dict[str, any]:
        """
        获取 Comment 互动数据
        
        Args:
            comment_id: Comment ID
            
        Returns:
            互动数据 {"likes_received": int, "replies": int, "content_length": int}
        """
        try:
            comment_data = self.get_comment(comment_id)
            
            if not comment_data:
                return {
                    "likes_received": 0,
                    "replies": 0,
                    "content_length": 0,
                    "comment_id": comment_id
                }

            # 提取互动数据
            interactions = {
                "likes_received": comment_data.get("score", 0),
                "replies": comment_data.get("replyCount", 0),
                "content_length": len(comment_data.get("content", "")),
                "comment_id": comment_id
            }

            logger.info(f"📊 Comment {comment_id} 互动数据:")
            logger.info(f"   Likes: {interactions['likes_received']}")
            logger.info(f"   Content: {interactions['content_length']} 字符")
            
            return interactions

        except Exception as e:
            logger.error(f"❌ 获取 Comment 互动数据错误: {e}")
            return {
                "likes_received": 0,
                "replies": 0,
                "content_length": 0,
                "comment_id": comment_id
            }

    def get_my_posts(
        self,
        agent_id: str,
        date: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict]:
        """
        获取我的 Posts 列表
        
        Args:
            agent_id: Agent ID
            date: 日期（YYYY-MM-DD），默认为今天
            limit: 返回数量限制
            
        Returns:
            Posts 列表
        """
        try:
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")

            url = f"{self.base_url}/community/posts"
            
            params = {
                "author": agent_id,
                "sort": "new",
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
                posts = data.get("posts", [])
                
                # 按日期过滤
                if date:
                    posts = [p for p in posts if date in p.get("createdAt", "")]
                
                logger.info(f"✅ 获取到 {len(posts)} 篇 Post（{date}）")
                return posts
            else:
                logger.warning(f"⚠️  Posts 列表请求失败: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"❌ 获取 Posts 列表错误: {e}")
            return []


class BotLearnMockClient:
    """
    BotLearn Mock 客户端（用于测试和 API 不可用时）
    返回模拟数据，使系统可以继续运行
    """

    def __init__(self):
        import random
        # 模拟数据存储
        self.mock_posts = {}
        self.mock_comments = {}

    def register_mock_post(
        self,
        post_id: str,
        mock_data: Dict = None
    ) -> None:
        """注册模拟 Post"""
        if mock_data is None:
            import random
            mock_data = {
                "score": random.randint(5, 20),
                "commentCount": random.randint(2, 8),
                "content": "This is a mock post about AI and productivity.",
                "viewCount": random.randint(50, 200)
            }
        
        self.mock_posts[post_id] = mock_data
        logger.info(f"📝 注册模拟 Post: {post_id}")

    def register_mock_comment(
        self,
        comment_id: str,
        mock_data: Dict = None
    ) -> None:
        """注册模拟 Comment"""
        if mock_data is None:
            import random
            mock_data = {
                "score": random.randint(1, 10),
                "replyCount": random.randint(0, 3),
                "content": "This is a mock comment with substantial content."
            }
        
        self.mock_comments[comment_id] = mock_data
        logger.info(f"📝 注册模拟 Comment: {comment_id}")

    def get_post_interactions(self, post_id: str) -> Dict[str, any]:
        """获取模拟 Post 互动数据"""
        if post_id in self.mock_posts:
            data = self.mock_posts[post_id]
            return {
                "likes_received": data.get("score", 0),
                "replies": data.get("commentCount", 0),
                "content_length": len(data.get("content", "")),
                "post_id": post_id,
                "mock": True
            }
        else:
            return {
                "likes_received": 8,
                "replies": 3,
                "content_length": 150,
                "post_id": post_id,
                "mock": True
            }

    def get_comment_interactions(self, comment_id: str) -> Dict[str, any]:
        """获取模拟 Comment 互动数据"""
        if comment_id in self.mock_comments:
            data = self.mock_comments[comment_id]
            return {
                "likes_received": data.get("score", 0),
                "replies": data.get("replyCount", 0),
                "content_length": len(data.get("content", "")),
                "comment_id": comment_id,
                "mock": True
            }
        else:
            return {
                "likes_received": 2,
                "replies": 0,
                "content_length": 80,
                "comment_id": comment_id,
                "mock": True
            }


# 全局客户端实例
_botlearn_client = None
_botlearn_mock_client = BotLearnMockClient()


def init_botlearn_client(api_key: Optional[str] = None, use_mock: bool = False) -> None:
    """
    初始化 BotLearn 客户端
    
    Args:
        api_key: API Key
        use_mock: 是否使用 Mock 客户端
    """
    global _botlearn_client, _botlearn_mock_client
    
    if use_mock:
        logger.info("🧪 使用 BotLearn Mock 客户端")
        _botlearn_client = _botlearn_mock_client
    else:
        if not api_key:
            logger.warning("⚠️  未提供 API Key，使用 Mock 客户端")
            _botlearn_client = _botlearn_mock_client
        else:
            _botlearn_client = BotLearnClient(api_key)


def get_botlearn_client() -> BotLearnClient:
    """获取全局 BotLearn 客户端"""
    return _botlearn_client


# 便捷函数
def get_post_interactions(post_id: str) -> Dict[str, any]:
    """获取 Post 互动数据（便捷函数）"""
    client = get_botlearn_client()
    return client.get_post_interactions(post_id)


def get_comment_interactions(comment_id: str) -> Dict[str, any]:
    """获取 Comment 互动数据（便捷函数）"""
    client = get_botlearn_client()
    return client.get_comment_interactions(comment_id)


if __name__ == "__main__":
    # 测试代码
    print("\n🧪 测试 BotLearn Mock 客户端...")
    
    # 初始化 Mock 客户端
    init_botlearn_client(use_mock=True)
    
    # 注册模拟数据
    mock_client = get_botlearn_client()
    mock_client.register_mock_post("post-001", {
        "score": 15,
        "commentCount": 5,
        "content": "AI productivity is key to modern work. Here are 5 tips to improve your workflow..." * 2
    })
    
    mock_client.register_mock_comment("comment-001", {
        "score": 7,
        "replyCount": 1,
        "content": "These are great tips! I especially like #3 about automating repetitive tasks."
    })
    
    # 获取互动数据
    post_interactions = get_post_interactions("post-001")
    print(f"   Post 互动数据: {json.dumps(post_interactions, indent=2)}")
    
    comment_interactions = get_comment_interactions("comment-001")
    print(f"   Comment 互动数据: {json.dumps(comment_interactions, indent=2)}")
