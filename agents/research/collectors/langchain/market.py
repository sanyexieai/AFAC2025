from typing import Dict, List, Any, Optional
import json
from datetime import datetime
from langchain.tools import BaseTool
from langchain_community.tools import TavilySearchResults
from .base import LangChainCollector

class MarketDataTool(BaseTool):
    """市场数据工具"""
    name: str = "market_data_tool"
    description: str = "获取市场数据"
    max_results: int = 5
    tavily_search: Optional[TavilySearchResults] = None
    
    def __init__(self, max_results: int = 5):
        super().__init__()
        self.max_results = max_results
        self.tavily_search = TavilySearchResults(max_results=max_results)
    
    def _run(self, target: str, timeframe: str, fields: Optional[List[str]] = None) -> str:
        """执行搜索
        
        Args:
            target: 目标（公司/行业）
            timeframe: 时间范围
            fields: 需要的字段列表
            
        Returns:
            str: JSON 格式的市场数据
        """
        # 构建搜索查询
        query = f"{target} {timeframe} 股票行情 开盘价 收盘价 最高价 最低价 成交量"
        results = self.tavily_search.invoke(query)
        
        # 处理搜索结果
        market_data = {
            "target": target,
            "timeframe": timeframe,
            "data": {
                "open": 100.0,  # 示例数据
                "close": 102.0,
                "high": 105.0,
                "low": 98.0,
                "volume": 1000000
            },
            "sources": []
        }
        
        # 添加来源信息
        for result in results:
            market_data["sources"].append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", "")[:200]  # 限制内容长度
            })
        
        return json.dumps(market_data, ensure_ascii=False, indent=2)

class MarketNewsTool(BaseTool):
    """市场新闻工具"""
    name: str = "market_news_tool"
    description: str = "获取市场新闻"
    max_results: int = 5
    tavily_search: Optional[TavilySearchResults] = None
    
    def __init__(self, max_results: int = 5):
        super().__init__()
        self.max_results = max_results
        self.tavily_search = TavilySearchResults(max_results=max_results)
    
    def _run(self, target: str, timeframe: str) -> str:
        """执行搜索
        
        Args:
            target: 目标（公司/行业）
            timeframe: 时间范围
            
        Returns:
            str: JSON 格式的新闻数据
        """
        # 构建搜索查询
        query = f"{target} {timeframe} 市场新闻 分析 评论"
        results = self.tavily_search.invoke(query)
        
        # 处理搜索结果
        news_data = {
            "target": target,
            "timeframe": timeframe,
            "news": []
        }
        
        for result in results:
            news_data["news"].append({
                "title": result.get("title", ""),
                "content": result.get("content", "")[:200],  # 限制内容长度
                "url": result.get("url", ""),
                "source": result.get("source", "")
            })
        
        return json.dumps(news_data, ensure_ascii=False, indent=2)

class LangChainMarketCollector(LangChainCollector):
    """基于 LangChain 的市场数据采集器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.llm = config.get("llm")
        if not self.llm:
            raise ValueError("LLM 配置缺失")
        self._setup_tools()
    
    def _setup_tools(self) -> None:
        """设置工具集"""
        self.market_data_tool = MarketDataTool(max_results=self.config.get("max_results", 5))
        self.market_news_tool = MarketNewsTool(max_results=self.config.get("max_results", 5))
    
    def _get_system_prompt(self) -> str:
        return """你是一个专业的市场数据采集助手。你的任务是：
1. 使用市场数据工具搜索股票行情数据
2. 使用市场新闻工具搜索相关新闻
3. 确保数据的准确性和时效性
4. 按照指定格式返回结果"""
    
    def collect(self, target: str, timeframe: str, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """收集市场数据
        
        Args:
            target: 股票代码
            timeframe: 时间范围
            fields: 需要的字段列表
            
        Returns:
            Dict: 市场数据
        """
        self.logger.info(f"开始收集市场数据: target={target}, timeframe={timeframe}")
        
        # 使用 Agent 执行数据采集
        result = self.agent_executor.invoke({
            "input": f"搜索 {target} 的{timeframe or '最新'}市场数据和相关新闻",
            "chat_history": []  # 添加空的聊天历史
        })
        
        # 解析结果
        try:
            market_data = json.loads(result["output"])
            if not self.validate(market_data):
                raise ValueError("市场数据验证失败")
            return market_data
        except Exception as e:
            self.logger.error(f"市场数据收集失败: {str(e)}")
            raise
    
    def validate(self, data: Dict) -> bool:
        """验证市场数据
        
        Args:
            data: 待验证的数据
            
        Returns:
            bool: 验证是否通过
        """
        try:
            # 检查必要字段
            if not all(key in data for key in ["target", "timeframe", "data", "sources"]):
                return False
            
            # 检查数据字段
            required_fields = ["open", "close", "high", "low", "volume"]
            if not all(field in data["data"] for field in required_fields):
                return False
            
            # 检查数据类型
            for field in required_fields:
                if data["data"][field] is not None and not isinstance(data["data"][field], (int, float)):
                    return False
            
            # 检查数据合理性
            if all(data["data"][field] is not None for field in required_fields):
                if data["data"]["high"] < data["data"]["low"]:
                    return False
                if data["data"]["high"] < data["data"]["open"]:
                    return False
                if data["data"]["high"] < data["data"]["close"]:
                    return False
                if data["data"]["low"] > data["data"]["open"]:
                    return False
                if data["data"]["low"] > data["data"]["close"]:
                    return False
                if data["data"]["volume"] < 0:
                    return False
            
            # 检查数据来源
            if not isinstance(data["sources"], list):
                return False
            for source in data["sources"]:
                if not all(key in source for key in ["title", "url", "content"]):
                    return False
            
            return True
        except Exception as e:
            self.logger.error(f"市场数据验证失败: {str(e)}")
            return False 