from typing import Dict, List, Any, Optional
import json
from langchain.tools import BaseTool
from langchain_community.tools import TavilySearchResults

class MacroDataTool(BaseTool):
    """宏观经济数据工具"""
    name: str = "macro_data_tool"
    description: str = "获取宏观经济数据"
    max_results: int = 5
    tavily_search: Optional[TavilySearchResults] = None
    
    def __init__(self, max_results: int = 5):
        super().__init__()
        self.max_results = max_results
        self.tavily_search = TavilySearchResults(max_results=max_results)
    
    def _run(self, target: str, timeframe: str, fields: Optional[List[str]] = None) -> str:
        """执行搜索
        
        Args:
            target: 目标（行业/主题）
            timeframe: 时间范围
            fields: 需要的字段列表
            
        Returns:
            str: JSON 格式的宏观经济数据
        """
        # 构建搜索查询
        query = f"{target} {timeframe} 宏观经济 政策 趋势 分析"
        results = self.tavily_search.invoke(query)
        
        # 处理搜索结果
        macro_data = {
            "target": target,
            "timeframe": timeframe,
            "data": {
                "gdp_growth": 5.5,  # 示例数据
                "inflation_rate": 2.1,
                "interest_rate": 3.5,
                "unemployment_rate": 4.2
            },
            "sources": []
        }
        
        # 添加来源信息
        for result in results:
            macro_data["sources"].append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", "")[:200]  # 限制内容长度
            })
        
        return json.dumps(macro_data, ensure_ascii=False, indent=2)

class MacroNewsTool(BaseTool):
    """宏观经济新闻工具"""
    name: str = "macro_news_tool"
    description: str = "获取宏观经济新闻"
    max_results: int = 5
    tavily_search: Optional[TavilySearchResults] = None
    
    def __init__(self, max_results: int = 5):
        super().__init__()
        self.max_results = max_results
        self.tavily_search = TavilySearchResults(max_results=max_results)
    
    def _run(self, target: str, timeframe: str) -> str:
        """执行搜索
        
        Args:
            target: 目标（行业/主题）
            timeframe: 时间范围
            
        Returns:
            str: JSON 格式的新闻数据
        """
        # 构建搜索查询
        query = f"{target} {timeframe} 宏观经济新闻 政策解读 趋势分析"
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

class LangChainMacroCollector:
    """使用 LangChain 的宏观经济数据收集器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._setup_tools()
    
    def _setup_tools(self):
        self.macro_data_tool = MacroDataTool(max_results=self.config.get("max_results", 5))
        self.macro_news_tool = MacroNewsTool(max_results=self.config.get("max_results", 5))
    
    def collect(self, target: str, timeframe: str, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        try:
            # 获取宏观经济数据
            macro_data = json.loads(self.macro_data_tool._run(target, timeframe, fields))
            # 获取宏观经济新闻
            news_data = json.loads(self.macro_news_tool._run(target, timeframe))
            # 合并数据
            result = {
                "target": target,
                "timeframe": timeframe,
                "macro_data": macro_data["data"],
                "news": news_data["news"],
                "sources": macro_data["sources"]
            }
            self.validate(result)
            return result
        except Exception as e:
            raise Exception(f"Error collecting macro data: {str(e)}")
    
    def validate(self, data: Dict[str, Any]) -> bool:
        # 检查必要字段
        if not all(key in data for key in ["target", "timeframe", "macro_data", "news"]):
            raise ValueError("Missing required fields")
        # 检查数据类型
        if not isinstance(data["macro_data"], dict):
            raise ValueError("Macro data must be a dictionary")
        if not isinstance(data["news"], list):
            raise ValueError("News must be a list")
        return True 