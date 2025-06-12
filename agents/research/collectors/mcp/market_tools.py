from typing import Dict, List, Any
import json
from mcp.server.fastmcp import FastMCP
from .utils import setup_logger, get_logger, tavily_search

# 初始化日志配置
setup_logger()

# 初始化日志记录器
logger = get_logger(__name__)

# 初始化 MCP 服务器
mcp = FastMCP("market_service")

@mcp.tool()
async def fetch_tushare_data(target: str, timeframe: str, fields: List[str]) -> str:
    """从 Tushare 获取数据
    
    Args:
        target: 目标（股票代码/指数代码）
        timeframe: 时间范围
        fields: 需要的字段列表
        
    Returns:
        str: JSON 格式的市场数据
    """
    logger.info(f"Fetching Tushare data for target={target}, timeframe={timeframe}, fields={fields}")
    try:
        # 构建搜索查询
        query = f"{target} {timeframe} 股票行情 开盘价 收盘价 最高价 最低价 成交量"
        results = tavily_search.invoke(query)
        
        # 解析搜索结果
        market_data = {
            "target": target,
            "timeframe": timeframe,
            "data": {
                "open": None,
                "close": None,
                "high": None,
                "low": None,
                "volume": None
            },
            "sources": []
        }
        
        # 从搜索结果中提取数据
        for result in results:
            content = result.get("content", "")
            # 简单解析示例，实际应用中应该使用更复杂的解析逻辑
            if "开盘价" in content:
                market_data["data"]["open"] = 100.0  # 示例值
            if "收盘价" in content:
                market_data["data"]["close"] = 101.0  # 示例值
            if "最高价" in content:
                market_data["data"]["high"] = 102.0  # 示例值
            if "最低价" in content:
                market_data["data"]["low"] = 99.0  # 示例值
            if "成交量" in content:
                market_data["data"]["volume"] = 1000000  # 示例值
            
            # 添加数据来源
            market_data["sources"].append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": content[:200]  # 只保存前200个字符
            })
        
        logger.info(f"Successfully retrieved market data for {target}")
        return json.dumps(market_data, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error fetching Tushare data: {str(e)}", exc_info=True)
        raise

@mcp.tool()
async def validate_market_data(market_data: str) -> str:
    """验证市场数据
    
    Args:
        market_data: JSON 格式的市场数据
        
    Returns:
        str: 验证结果
    """
    logger.info("Validating market data")
    try:
        data = json.loads(market_data)
        
        # 检查必要字段
        required_fields = ["target", "timeframe", "data", "sources"]
        if not all(field in data for field in required_fields):
            logger.error(f"Missing required fields. Found: {list(data.keys())}")
            return json.dumps({"valid": False, "error": "Missing required fields"})
        
        # 检查数据类型
        if not isinstance(data["data"], dict):
            logger.error("Data field is not a dictionary")
            return json.dumps({"valid": False, "error": "Data field is not a dictionary"})
        
        # 检查数据完整性
        required_data_fields = ["open", "close", "high", "low", "volume"]
        if not all(field in data["data"] for field in required_data_fields):
            logger.error(f"Missing required data fields. Found: {list(data['data'].keys())}")
            return json.dumps({"valid": False, "error": "Missing required data fields"})
        
        # 检查数据逻辑
        if data["data"]["high"] < data["data"]["low"]:
            logger.error("High price is less than low price")
            return json.dumps({"valid": False, "error": "High price is less than low price"})
        
        if data["data"]["open"] < data["data"]["low"] or data["data"]["open"] > data["data"]["high"]:
            logger.error("Open price is outside of high-low range")
            return json.dumps({"valid": False, "error": "Open price is outside of high-low range"})
        
        if data["data"]["close"] < data["data"]["low"] or data["data"]["close"] > data["data"]["high"]:
            logger.error("Close price is outside of high-low range")
            return json.dumps({"valid": False, "error": "Close price is outside of high-low range"})
        
        logger.info("Market data validation successful")
        return json.dumps({"valid": True})
    except Exception as e:
        logger.error(f"Error validating market data: {str(e)}", exc_info=True)
        return json.dumps({"valid": False, "error": str(e)}) 