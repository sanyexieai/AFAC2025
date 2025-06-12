from typing import Dict, List, Any
from datetime import datetime
import json
from mcp.server.fastmcp import FastMCP
from .utils import setup_logger, get_logger, tavily_search

# 初始化日志配置
setup_logger()

# 初始化日志记录器
logger = get_logger(__name__)

# 初始化 MCP 服务器
mcp = FastMCP("news_service")

@mcp.tool()
async def fetch_sina_news(target: str, timeframe: str, fields: List[str]) -> str:
    """从新浪新闻获取数据
    
    Args:
        target: 目标（公司/行业）
        timeframe: 时间范围
        fields: 需要的字段列表
        
    Returns:
        str: JSON 格式的新闻数据
    """
    logger.info(f"Fetching Sina news for target={target}, timeframe={timeframe}, fields={fields}")
    try:
        # 构建搜索查询
        query = f"site:sina.com.cn {target} {timeframe} 新闻"
        results = tavily_search.invoke(query)
        
        # 格式化结果
        news_list = []
        for result in results:
            news = {
                "title": result.get("title", ""),
                "content": result.get("content", ""),
                "source": "新浪财经",
                "url": result.get("url", ""),
                "publish_time": datetime.now().isoformat(),  # 注意：实际应用中应该从内容中提取时间
                "sentiment": 0.8  # 注意：实际应用中应该使用情感分析
            }
            news_list.append(news)
        
        data = {
            "target": target,
            "timeframe": timeframe,
            "news": news_list
        }
        
        logger.info(f"Successfully retrieved {len(news_list)} news items from Sina")
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error fetching Sina news: {str(e)}", exc_info=True)
        raise

@mcp.tool()
async def fetch_eastmoney_news(target: str, timeframe: str, fields: List[str]) -> str:
    """从东方财富获取数据
    
    Args:
        target: 目标（公司/行业）
        timeframe: 时间范围
        fields: 需要的字段列表
        
    Returns:
        str: JSON 格式的新闻数据
    """
    logger.info(f"Fetching EastMoney news for target={target}, timeframe={timeframe}, fields={fields}")
    try:
        # 构建搜索查询
        query = f"site:eastmoney.com {target} {timeframe} 新闻"
        results = tavily_search.invoke(query)
        
        # 格式化结果
        news_list = []
        for result in results:
            news = {
                "title": result.get("title", ""),
                "content": result.get("content", ""),
                "source": "东方财富",
                "url": result.get("url", ""),
                "publish_time": datetime.now().isoformat(),  # 注意：实际应用中应该从内容中提取时间
                "sentiment": 0.9  # 注意：实际应用中应该使用情感分析
            }
            news_list.append(news)
        
        data = {
            "target": target,
            "timeframe": timeframe,
            "news": news_list
        }
        
        logger.info(f"Successfully retrieved {len(news_list)} news items from EastMoney")
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error fetching EastMoney news: {str(e)}", exc_info=True)
        raise

@mcp.tool()
async def filter_news(news_data: str, filters: Dict[str, Any]) -> str:
    """过滤新闻数据
    
    Args:
        news_data: JSON 格式的新闻数据
        filters: 过滤条件
        
    Returns:
        str: 过滤后的新闻数据
    """
    logger.info(f"Filtering news data with filters: {filters}")
    try:
        data = json.loads(news_data)
        if not filters:
            return news_data
        
        filtered_news = []
        for news in data["news"]:
            if all(_apply_filter(news, key, value) 
                  for key, value in filters.items()):
                filtered_news.append(news)
        
        data["news"] = filtered_news
        logger.info(f"Filtered to {len(filtered_news)} news items")
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error filtering news data: {str(e)}", exc_info=True)
        raise

@mcp.tool()
async def aggregate_news(news_data: str, aggregation: Dict[str, str]) -> str:
    """聚合新闻数据
    
    Args:
        news_data: JSON 格式的新闻数据
        aggregation: 聚合规则
        
    Returns:
        str: 聚合后的新闻数据
    """
    logger.info(f"Aggregating news data with rules: {aggregation}")
    try:
        data = json.loads(news_data)
        if not aggregation:
            return news_data
        
        result = {}
        for field, rule in aggregation.items():
            if rule == "count":
                result[f"{field}_count"] = len(data["news"])
            elif rule == "average":
                values = [news[field] for news in data["news"] if field in news]
                if values:
                    result[f"{field}_avg"] = sum(values) / len(values)
        
        result["news"] = data["news"]
        logger.info("Successfully aggregated news data")
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error aggregating news data: {str(e)}", exc_info=True)
        raise

@mcp.tool()
async def enrich_news(news_data: str) -> str:
    """丰富新闻数据
    
    Args:
        news_data: JSON 格式的新闻数据
        
    Returns:
        str: 丰富后的新闻数据
    """
    logger.info("Enriching news data")
    try:
        data = json.loads(news_data)
        for news in data["news"]:
            # 添加时间戳
            if "publish_time" in news:
                news["timestamp"] = datetime.fromisoformat(news["publish_time"]).timestamp()
            # 添加来源信息
            if "source" in news:
                news["source_info"] = {
                    "name": news["source"],
                    "reliability": _get_source_reliability(news["source"])
                }
        
        logger.info("Successfully enriched news data")
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error enriching news data: {str(e)}", exc_info=True)
        raise

@mcp.tool()
async def validate_news(news_data: str) -> str:
    """验证新闻数据
    
    Args:
        news_data: JSON 格式的新闻数据
        
    Returns:
        str: 验证结果
    """
    logger.info("Validating news data")
    try:
        data = json.loads(news_data)
        
        # 检查必要字段
        required_fields = ["target", "timeframe", "news"]
        if not all(field in data for field in required_fields):
            logger.error(f"Missing required fields. Found: {list(data.keys())}")
            return json.dumps({"valid": False, "error": "Missing required fields"})
        
        # 检查新闻列表
        if not isinstance(data["news"], list):
            logger.error("News field is not a list")
            return json.dumps({"valid": False, "error": "News field is not a list"})
        
        # 检查每条新闻的字段
        for i, news in enumerate(data["news"]):
            required_news_fields = ["title", "content", "source", "publish_time", "sentiment"]
            if not all(field in news for field in required_news_fields):
                logger.error(f"News item {i} missing required fields. Found: {list(news.keys())}")
                return json.dumps({"valid": False, "error": f"News item {i} missing required fields"})
        
        logger.info("News data validation successful")
        return json.dumps({"valid": True})
    except Exception as e:
        logger.error(f"Error validating news data: {str(e)}", exc_info=True)
        return json.dumps({"valid": False, "error": str(e)})

def _apply_filter(news: Dict, key: str, value: Any) -> bool:
    """应用单个过滤条件"""
    if key not in news:
        return False
    if isinstance(value, (list, tuple)):
        return news[key] in value
    return news[key] == value

def _get_source_reliability(source: str) -> float:
    """获取新闻来源的可靠性评分"""
    # TODO: 实现实际的可靠性评分逻辑
    return 0.8