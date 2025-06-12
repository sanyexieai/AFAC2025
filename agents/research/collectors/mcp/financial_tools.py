from typing import Dict, List, Any
import json
from mcp.server.fastmcp import FastMCP
from .utils import setup_logger, get_logger, tavily_search

# 初始化日志配置
setup_logger()

# 初始化日志记录器
logger = get_logger(__name__)

# 初始化 MCP 服务器
mcp = FastMCP("financial_service")

@mcp.tool()
async def fetch_financial_data(target: str, timeframe: str, fields: List[str]) -> str:
    """获取财务数据
    
    Args:
        target: 目标（公司代码）
        timeframe: 时间范围
        fields: 需要的字段列表
        
    Returns:
        str: JSON 格式的财务数据
    """
    logger.info(f"Fetching financial data for target={target}, timeframe={timeframe}, fields={fields}")
    try:
        # 构建搜索查询
        query = f"{target} {timeframe} 财务报告 营业收入 净利润 每股收益 净资产收益率"
        results = tavily_search.invoke(query)
        
        # 解析搜索结果
        financial_data = {
            "target": target,
            "timeframe": timeframe,
            "data": {
                "revenue": None,  # 营业收入
                "net_profit": None,  # 净利润
                "eps": None,  # 每股收益
                "roe": None  # 净资产收益率
            },
            "sources": []
        }
        
        # 从搜索结果中提取数据
        for result in results:
            content = result.get("content", "")
            # 简单解析示例，实际应用中应该使用更复杂的解析逻辑
            if "营业收入" in content:
                financial_data["data"]["revenue"] = 1000000000  # 示例值
            if "净利润" in content:
                financial_data["data"]["net_profit"] = 100000000  # 示例值
            if "每股收益" in content:
                financial_data["data"]["eps"] = 1.5  # 示例值
            if "净资产收益率" in content:
                financial_data["data"]["roe"] = 15.0  # 示例值
            
            # 添加数据来源
            financial_data["sources"].append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": content[:200]  # 只保存前200个字符
            })
        
        logger.info(f"Successfully retrieved financial data for {target}")
        return json.dumps(financial_data, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error fetching financial data: {str(e)}", exc_info=True)
        raise

@mcp.tool()
async def validate_financial_data(financial_data: str) -> str:
    """验证财务数据
    
    Args:
        financial_data: JSON 格式的财务数据
        
    Returns:
        str: 验证结果
    """
    logger.info("Validating financial data")
    try:
        data = json.loads(financial_data)
        
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
        required_data_fields = ["revenue", "net_profit", "eps", "roe"]
        if not all(field in data["data"] for field in required_data_fields):
            logger.error(f"Missing required data fields. Found: {list(data['data'].keys())}")
            return json.dumps({"valid": False, "error": "Missing required data fields"})
        
        # 检查数据逻辑
        if data["data"]["revenue"] is not None and data["data"]["revenue"] < 0:
            logger.error("Revenue cannot be negative")
            return json.dumps({"valid": False, "error": "Revenue cannot be negative"})
        
        if data["data"]["eps"] is not None and data["data"]["eps"] < 0:
            logger.error("EPS cannot be negative")
            return json.dumps({"valid": False, "error": "EPS cannot be negative"})
        
        if data["data"]["roe"] is not None and (data["data"]["roe"] < 0 or data["data"]["roe"] > 100):
            logger.error("ROE must be between 0 and 100")
            return json.dumps({"valid": False, "error": "ROE must be between 0 and 100"})
        
        logger.info("Financial data validation successful")
        return json.dumps({"valid": True})
    except Exception as e:
        logger.error(f"Error validating financial data: {str(e)}", exc_info=True)
        return json.dumps({"valid": False, "error": str(e)}) 