from typing import Dict, List, Any, Optional
import json
from datetime import datetime
from langchain.tools import BaseTool
from langchain_community.tools import TavilySearchResults
from .base import LangChainCollector

class FinancialDataTool(BaseTool):
    """财务数据工具"""
    name: str = "financial_data_tool"
    description: str = "获取财务数据"
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
            str: JSON 格式的财务数据
        """
        # 构建搜索查询
        query = f"{target} {timeframe} 财务报告 营业收入 净利润 每股收益 净资产收益率"
        results = self.tavily_search.invoke(query)
        
        # 处理搜索结果
        financial_data = {
            "target": target,
            "timeframe": timeframe,
            "data": {
                "revenue": 1000000.0,  # 示例数据
                "net_profit": 100000.0,
                "eps": 1.0,
                "roe": 15.0
            },
            "sources": []
        }
        
        # 添加来源信息
        for result in results:
            financial_data["sources"].append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", "")[:200]  # 限制内容长度
            })
        
        return json.dumps(financial_data, ensure_ascii=False, indent=2)

class FinancialNewsTool(BaseTool):
    """财务新闻工具"""
    name: str = "financial_news_tool"
    description: str = "获取财务新闻"
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
        query = f"{target} {timeframe} 财务新闻 分析 评论"
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

class LangChainFinancialCollector(LangChainCollector):
    """使用 LangChain 的财务数据收集器"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化收集器
        
        Args:
            config: 配置信息
        """
        super().__init__(config)
        self.llm = config.get("llm")
        if not self.llm:
            raise ValueError("LLM 配置缺失")
        self._setup_tools()
    
    def _setup_tools(self):
        """设置工具"""
        self.financial_data_tool = FinancialDataTool(max_results=5)
        self.financial_news_tool = FinancialNewsTool(max_results=5)
    
    def _get_system_prompt(self) -> str:
        """获取系统提示"""
        return """你是一个财务数据收集助手。你的任务是：
1. 搜索财务数据，包括营业收入、净利润、每股收益和净资产收益率
2. 搜索财务相关的新闻
3. 确保数据的准确性和完整性
4. 提供数据来源信息"""
    
    def collect(self, target: str, timeframe: str, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """收集财务数据
        
        Args:
            target: 目标（公司代码）
            timeframe: 时间范围
            fields: 需要的字段列表
            
        Returns:
            Dict[str, Any]: 财务数据
        """
        self.logger.info(f"开始收集财务数据: target={target}, timeframe={timeframe}")
        
        try:
            # 获取财务数据
            financial_data = json.loads(self.financial_data_tool._run(target, timeframe, fields))
            
            # 获取财务新闻
            news_data = json.loads(self.financial_news_tool._run(target, timeframe))
            
            # 合并数据
            result = {
                "target": target,
                "timeframe": timeframe,
                "financial_data": financial_data["data"],
                "news": news_data["news"],
                "sources": financial_data["sources"]
            }
            
            # 验证数据
            self.validate(result)
            
            return result
        except Exception as e:
            self.logger.error(f"财务数据收集失败: {str(e)}")
            raise
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """验证财务数据
        
        Args:
            data: 财务数据
            
        Returns:
            bool: 验证结果
        """
        # 检查必要字段
        if not all(key in data for key in ["target", "timeframe", "financial_data", "news"]):
            raise ValueError("Missing required fields")
        
        # 检查财务数据
        financial_data = data["financial_data"]
        if not all(key in financial_data for key in ["revenue", "net_profit", "eps", "roe"]):
            raise ValueError("Missing required financial data fields")
        
        # 检查数据类型
        if not isinstance(financial_data, dict):
            raise ValueError("Financial data must be a dictionary")
        
        # 检查数据逻辑
        if financial_data["revenue"] is not None and financial_data["revenue"] < 0:
            raise ValueError("Revenue cannot be negative")
        
        if financial_data["eps"] is not None and financial_data["eps"] < 0:
            raise ValueError("EPS cannot be negative")
        
        if financial_data["roe"] is not None and (financial_data["roe"] < 0 or financial_data["roe"] > 100):
            raise ValueError("ROE must be between 0 and 100")
        
        return True 