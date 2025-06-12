from typing import Dict, List, Any, Optional
import json
import os
from langchain.tools import BaseTool
from langchain_community.tools import TavilySearchResults
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from .base import LangChainCollector
from langchain_community.chat_models import ChatOpenAI
from langchain.schema.runnable import Runnable

class NewsSearchTool(BaseTool):
    """新闻搜索工具"""
    name: str = "news_search_tool"
    description: str = "搜索相关新闻"
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
        query = f"{target} {timeframe} 新闻 报道 分析"
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

class NewsSummarizerTool(BaseTool):
    """新闻摘要工具"""
    name: str = "news_summarizer_tool"
    description: str = "生成新闻摘要"
    max_results: int = 5
    tavily_search: Optional[TavilySearchResults] = None
    llm: Optional[Runnable] = None
    
    def __init__(self, llm: Runnable, max_results: int = 5):
        super().__init__()
        self.max_results = max_results
        self.tavily_search = TavilySearchResults(max_results=max_results)
        self.llm = llm
    
    def _run(self, target: str, timeframe: str) -> str:
        """执行摘要生成
        
        Args:
            target: 目标（行业/主题）
            timeframe: 时间范围
            
        Returns:
            str: JSON 格式的摘要数据
        """
        if not self.llm:
            raise ValueError("LLM not initialized")
            
        # 构建搜索查询
        query = f"{target} {timeframe} 新闻 报道 分析"
        results = self.tavily_search.invoke(query)
        
        # 处理搜索结果
        summary_data = {
            "target": target,
            "timeframe": timeframe,
            "summaries": []
        }
        
        for result in results:
            # 创建文档
            doc = Document(page_content=result.get("content", ""))
            # 分割文本
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
            texts = text_splitter.split_documents([doc])
            # 生成摘要
            chain = load_summarize_chain(self.llm, chain_type="map_reduce")
            summary = chain.run(texts)
            
            summary_data["summaries"].append({
                "title": result.get("title", ""),
                "summary": summary,
                "url": result.get("url", ""),
                "source": result.get("source", "")
            })
        
        return json.dumps(summary_data, ensure_ascii=False, indent=2)

class LangChainNewsCollector(LangChainCollector):
    """基于 LangChain 的新闻数据采集器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._setup_tools()
    
    def _setup_tools(self) -> None:
        """设置工具集"""
        # 确保使用 ChatOpenAI
        if isinstance(self.config.get("llm"), ChatOpenAI):
            llm = self.config["llm"]
        else:
            llm = ChatOpenAI(
                model_name=os.getenv("OPENAI_API_MODEL", "deepseek-chat"),
                temperature=self.config.get("temperature", 0.7),
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_API_BASE")
            )
            
        self.news_search_tool = NewsSearchTool(max_results=self.config.get("max_results", 5))
        self.news_summarizer_tool = NewsSummarizerTool(
            llm=llm,
            max_results=self.config.get("max_results", 5)
        )
    
    def _get_system_prompt(self) -> str:
        return """你是一个专业的新闻数据采集助手。你的任务是：
1. 使用新闻搜索工具搜索相关新闻
2. 使用新闻摘要工具生成新闻摘要
3. 确保新闻的时效性和相关性
4. 按照指定格式返回结果"""
    
    def collect(self, target: str, timeframe: str, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """收集新闻数据
        
        Args:
            target: 目标（行业/主题）
            timeframe: 时间范围
            fields: 需要的字段列表
            
        Returns:
            Dict[str, Any]: 收集到的新闻数据
        """
        self.logger.info(f"开始收集新闻数据: target={target}, timeframe={timeframe}")
        
        try:
            # 获取新闻数据
            news_data = json.loads(self.news_search_tool._run(target, timeframe))
            # 获取新闻摘要
            summary_data = json.loads(self.news_summarizer_tool._run(target, timeframe))
            
            # 处理字段过滤
            if fields:
                for news in news_data["news"]:
                    news.update({field: news.get(field, "") for field in fields if field not in news})
                for summary in summary_data["summaries"]:
                    summary.update({field: summary.get(field, "") for field in fields if field not in summary})
            
            # 合并数据
            result = {
                "target": target,
                "timeframe": timeframe,
                "news": news_data["news"],
                "summaries": summary_data["summaries"]
            }
            self.validate(result)
            return result
        except Exception as e:
            self.logger.error(f"新闻数据收集失败: {str(e)}")
            raise
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """验证新闻数据
        
        Args:
            data: 待验证的数据
            
        Returns:
            bool: 验证是否通过
        """
        try:
            # 检查必要字段
            if not all(key in data for key in ["target", "timeframe", "news", "summaries"]):
                raise ValueError("Missing required fields")
            
            # 检查新闻列表
            if not isinstance(data["news"], list):
                raise ValueError("News must be a list")
            
            # 检查摘要列表
            if not isinstance(data["summaries"], list):
                raise ValueError("Summaries must be a list")
            
            # 检查每条新闻的字段
            for news in data["news"]:
                if not all(key in news for key in ["title", "content", "source", "url"]):
                    raise ValueError("Missing required fields in news")
                
                # 检查时间格式
                try:
                    datetime.fromisoformat(news["publish_time"])
                except ValueError:
                    raise ValueError("Invalid publish_time format")
                
                # 检查 URL 格式
                if not news["url"].startswith(("http://", "https://")):
                    raise ValueError("Invalid URL format")
            
            # 检查每条摘要的字段
            for summary in data["summaries"]:
                if not all(key in summary for key in ["title", "summary", "source", "url"]):
                    raise ValueError("Missing required fields in summary")
                
                # 检查时间格式
                try:
                    datetime.fromisoformat(summary["publish_time"])
                except ValueError:
                    raise ValueError("Invalid publish_time format in summary")
                
                # 检查 URL 格式
                if not summary["url"].startswith(("http://", "https://")):
                    raise ValueError("Invalid URL format in summary")
            
            return True
        except Exception as e:
            self.logger.error(f"新闻数据验证失败: {str(e)}")
            return False 