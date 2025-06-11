from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import asyncio
from mcp.server.fastmcp import FastMCP

class NewsMCPServer:
    """新闻 MCP 服务器"""
    
    def __init__(self, name: str = "news_service"):
        """初始化 MCP 服务器
        
        Args:
            name: 服务名称
        """
        self.mcp = FastMCP(name)
        self._setup_handlers()
    
    def _setup_handlers(self):
        """设置消息处理器"""
        from .news_tools import (
            fetch_sina_news,
            fetch_eastmoney_news,
            filter_news,
            aggregate_news,
            enrich_news,
            validate_news
        )
        
        # 注册工具
        self.mcp.register_tool("fetch_sina_news", fetch_sina_news)
        self.mcp.register_tool("fetch_eastmoney_news", fetch_eastmoney_news)
        self.mcp.register_tool("filter_news", filter_news)
        self.mcp.register_tool("aggregate_news", aggregate_news)
        self.mcp.register_tool("enrich_news", enrich_news)
        self.mcp.register_tool("validate_news", validate_news)
    
    async def start(self, host: str = "localhost", port: int = 8000):
        """启动服务器
        
        Args:
            host: 主机地址
            port: 端口号
        """
        await self.mcp.start(host=host, port=port)
    
    async def stop(self):
        """停止服务器"""
        await self.mcp.stop()

class MarketMCPServer:
    """市场数据 MCP 服务器"""
    
    def __init__(self, name: str = "market_service"):
        """初始化 MCP 服务器
        
        Args:
            name: 服务名称
        """
        self.mcp = FastMCP(name)
        self._setup_handlers()
    
    def _setup_handlers(self):
        """设置消息处理器"""
        from .market_tools import (
            fetch_wind_data,
            fetch_tushare_data,
            validate_market_data
        )
        
        # 注册工具
        self.mcp.register_tool("fetch_wind_data", fetch_wind_data)
        self.mcp.register_tool("fetch_tushare_data", fetch_tushare_data)
        self.mcp.register_tool("validate_market_data", validate_market_data)
    
    async def start(self, host: str = "localhost", port: int = 8001):
        """启动服务器
        
        Args:
            host: 主机地址
            port: 端口号
        """
        await self.mcp.start(host=host, port=port)
    
    async def stop(self):
        """停止服务器"""
        await self.mcp.stop()

class FinancialMCPServer:
    """财务数据 MCP 服务器"""
    
    def __init__(self, name: str = "financial_service"):
        """初始化 MCP 服务器
        
        Args:
            name: 服务名称
        """
        self.mcp = FastMCP(name)
        self._setup_handlers()
    
    def _setup_handlers(self):
        """设置消息处理器"""
        from .financial_tools import (
            fetch_financial_data,
            validate_financial_data
        )
        
        # 注册工具
        self.mcp.register_tool("fetch_financial_data", fetch_financial_data)
        self.mcp.register_tool("validate_financial_data", validate_financial_data)
    
    async def start(self, host: str = "localhost", port: int = 8002):
        """启动服务器
        
        Args:
            host: 主机地址
            port: 端口号
        """
        await self.mcp.start(host=host, port=port)
    
    async def stop(self):
        """停止服务器"""
        await self.mcp.stop()

async def start_all_servers():
    """启动所有 MCP 服务器"""
    news_server = NewsMCPServer()
    market_server = MarketMCPServer()
    financial_server = FinancialMCPServer()
    
    await asyncio.gather(
        news_server.start(),
        market_server.start(),
        financial_server.start()
    )
    
    return news_server, market_server, financial_server 