from typing import Dict, List, Any, Optional
import json
from langchain.tools import BaseTool
from langchain_community.tools import TavilySearchResults

class SearchTool(BaseTool):
    """搜索工具"""
    name: str = "search_tool"
    description: str = "执行网络搜索"
    max_results: int = 5
    tavily_search: Optional[TavilySearchResults] = None
    
    def __init__(self, max_results: int = 5):
        super().__init__()
        self.max_results = max_results
        self.tavily_search = TavilySearchResults(max_results=max_results)
    
    def _run(self, query: str) -> str:
        """执行搜索
        
        Args:
            query: 搜索查询
            
        Returns:
            str: JSON 格式的搜索结果
        """
        results = self.tavily_search.invoke(query)
        return json.dumps(results, ensure_ascii=False, indent=2)

class LangChainSearchCollector:
    """使用 LangChain 的搜索数据收集器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._setup_tools()
    
    def _setup_tools(self):
        self.search_tool = SearchTool(max_results=self.config.get("max_results", 5))
    
    def collect(self, target: str, timeframe: str, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        try:
            # 构建搜索查询
            query = f"{target} {timeframe}"
            if fields:
                query += f" {' '.join(fields)}"
            
            # 执行搜索
            results = json.loads(self.search_tool._run(query))
            
            # 验证结果
            self.validate(results)
            
            return results
        except Exception as e:
            raise Exception(f"Error collecting search data: {str(e)}")
    
    def validate(self, data: Dict[str, Any]) -> bool:
        # 检查必要字段
        if not isinstance(data, list):
            raise ValueError("Search results must be a list")
        # 检查每条结果的字段
        for result in data:
            if not all(key in result for key in ["title", "content", "url"]):
                raise ValueError("Search result missing required fields")
        return True 