from typing import Dict, List, Any
import json
from mcp.server.fastmcp import FastMCP
from .utils import setup_logger, get_logger, tavily_search

# 初始化日志配置
setup_logger()

# 初始化日志记录器
logger = get_logger(__name__)

# 初始化 MCP 服务器
mcp = FastMCP("search_service")

@mcp.tool()
async def search_web(query: str, max_results: int = 5) -> str:
    """使用 Tavily 搜索工具搜索网络
    
    Args:
        query: 搜索查询
        max_results: 最大结果数量
        
    Returns:
        str: JSON 格式的搜索结果
    """
    logger.info(f"Searching web for query: {query}")
    try:
        # 使用 Tavily 搜索
        results = tavily_search.invoke(query)
        
        # 格式化结果
        formatted_results = {
            "query": query,
            "results": results
        }
        
        logger.info(f"Found {len(results)} results")
        return json.dumps(formatted_results, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error searching web: {str(e)}", exc_info=True)
        raise

@mcp.tool()
async def filter_search_results(search_results: str, filters: Dict[str, Any]) -> str:
    """过滤搜索结果
    
    Args:
        search_results: JSON 格式的搜索结果
        filters: 过滤条件
        
    Returns:
        str: 过滤后的搜索结果
    """
    logger.info(f"Filtering search results with filters: {filters}")
    try:
        data = json.loads(search_results)
        if not filters:
            return search_results
        
        filtered_results = []
        for result in data["results"]:
            if all(_apply_filter(result, key, value) 
                  for key, value in filters.items()):
                filtered_results.append(result)
        
        data["results"] = filtered_results
        logger.info(f"Filtered to {len(filtered_results)} results")
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error filtering search results: {str(e)}", exc_info=True)
        raise

def _apply_filter(result: Dict, key: str, value: Any) -> bool:
    """应用单个过滤条件"""
    if key not in result:
        return False
    if isinstance(value, (list, tuple)):
        return result[key] in value
    return result[key] == value 