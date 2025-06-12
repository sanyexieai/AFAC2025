import logging
import sys
from typing import Dict, Any
from langchain_community.tools import TavilySearchResults

def setup_logger():
    """配置日志记录器"""
    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # 设置日志格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    # 获取根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # 清除现有的处理器
    root_logger.handlers = []
    
    # 添加控制台处理器
    root_logger.addHandler(console_handler)

# 初始化 Tavily 搜索工具
tavily_search = TavilySearchResults(max_results=5)

def get_logger(name: str) -> logging.Logger:
    """获取指定名称的日志记录器"""
    return logging.getLogger(name) 