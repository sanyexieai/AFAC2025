from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import asyncio
import logging
import sys
from .base import BaseCollector, DataSource
from .mcp import (
    fetch_sina_news,
    fetch_eastmoney_news,
    filter_news,
    aggregate_news,
    enrich_news,
    validate_news
)

# 配置日志
def setup_logger():
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

# 初始化日志配置
setup_logger()

class SinaNewsDataSource(DataSource):
    """新浪新闻数据源"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config.get('api_key')
        self.connected = True  # 默认设为可用
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"Initializing SinaNewsDataSource with config: {config}")
    
    def get_name(self) -> str:
        return "sina_news"
    
    def is_available(self) -> bool:
        available = self.connected
        self.logger.info(f"SinaNewsDataSource availability check: {available}")
        return available
    
    def get_data(self, target: str, timeframe: str, fields: List[str]) -> Dict:
        self.logger.info(f"Fetching data from Sina news for target={target}, timeframe={timeframe}, fields={fields}")
        # 创建事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # 获取数据
            self.logger.info("Calling fetch_sina_news")
            raw_data = loop.run_until_complete(fetch_sina_news(target, timeframe, fields))
            self.logger.info("Successfully got raw data from fetch_sina_news")
            data = json.loads(raw_data)
            
            # 验证数据
            self.logger.info("Validating news data")
            validation_result = loop.run_until_complete(validate_news(json.dumps(data)))
            validation_data = json.loads(validation_result)
            if not validation_data["valid"]:
                self.logger.error(f"News data validation failed: {validation_data}")
                raise ValueError("News data validation failed")
            
            self.logger.info("Data validation successful")
            return data
        except Exception as e:
            self.logger.error(f"Error in get_data: {str(e)}", exc_info=True)
            raise
        finally:
            loop.close()
    
    def get_metadata(self) -> Dict:
        return {
            "supported_fields": ["title", "content", "source", "publish_time", "sentiment"],
            "supported_timeframes": ["1d", "1w", "1m"],
            "rate_limit": 50
        }

class EastMoneyNewsDataSource(DataSource):
    """东方财富新闻数据源"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config.get('api_key')
        self.connected = True  # 默认设为可用
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"Initializing EastMoneyNewsDataSource with config: {config}")
    
    def get_name(self) -> str:
        return "eastmoney_news"
    
    def is_available(self) -> bool:
        available = self.connected
        self.logger.info(f"EastMoneyNewsDataSource availability check: {available}")
        return available
    
    def get_data(self, target: str, timeframe: str, fields: List[str]) -> Dict:
        self.logger.info(f"Fetching data from EastMoney news for target={target}, timeframe={timeframe}, fields={fields}")
        # 创建事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # 获取数据
            self.logger.info("Calling fetch_eastmoney_news")
            raw_data = loop.run_until_complete(fetch_eastmoney_news(target, timeframe, fields))
            self.logger.info("Successfully got raw data from fetch_eastmoney_news")
            data = json.loads(raw_data)
            
            # 验证数据
            self.logger.info("Validating news data")
            validation_result = loop.run_until_complete(validate_news(json.dumps(data)))
            validation_data = json.loads(validation_result)
            if not validation_data["valid"]:
                self.logger.error(f"News data validation failed: {validation_data}")
                raise ValueError("News data validation failed")
            
            self.logger.info("Data validation successful")
            return data
        except Exception as e:
            self.logger.error(f"Error in get_data: {str(e)}", exc_info=True)
            raise
        finally:
            loop.close()
    
    def get_metadata(self) -> Dict:
        return {
            "supported_fields": ["title", "content", "source", "publish_time", "sentiment"],
            "supported_timeframes": ["1d", "1w", "1m"],
            "rate_limit": 50
        }

class NewsDataCollector(BaseCollector):
    """新闻数据采集器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初始化新闻数据采集器
        
        Args:
            config: 配置信息，如果为None或为空则使用默认配置
        """
        # 初始化 logger
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 如果配置为空或None，使用默认配置
        if not config:
            config = {
                'sources': {
                    'sina_news': {'api_key': 'default'},
                    'eastmoney_news': {'api_key': 'default'}
                }
            }
            self.logger.info("Using default configuration")
        
        self.logger.info(f"Initializing NewsDataCollector with config: {config}")
        super().__init__(config)
    
    def _setup_sources(self) -> None:
        """初始化数据源"""
        # 从配置中加载数据源
        sources_config = self.config.get('sources', {})
        self.logger.info(f"Setting up news sources with config: {sources_config}")
        
        # 添加新浪新闻数据源
        if 'sina_news' in sources_config:
            self.logger.info("Initializing Sina news source")
            sina_source = SinaNewsDataSource(sources_config['sina_news'])
            self.register_source(sina_source)
            self.logger.info(f"Sina news source initialized and registered. Available: {sina_source.is_available()}")
        
        # 添加东方财富新闻数据源
        if 'eastmoney_news' in sources_config:
            self.logger.info("Initializing EastMoney news source")
            eastmoney_source = EastMoneyNewsDataSource(sources_config['eastmoney_news'])
            self.register_source(eastmoney_source)
            self.logger.info(f"EastMoney news source initialized and registered. Available: {eastmoney_source.is_available()}")
        
        self.logger.info(f"Total registered sources: {len(self.sources)}")
        for name, source in self.sources.items():
            self.logger.info(f"Source {name} available: {source.is_available()}")
    
    def _validate_impl(self, data: Dict) -> bool:
        """验证数据格式"""
        # 创建事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # 验证数据
            validation_result = loop.run_until_complete(validate_news(json.dumps(data)))
            return json.loads(validation_result)["valid"]
        finally:
            loop.close()
    
    def collect(self, target: str, timeframe: Optional[str] = None, fields: Optional[List[str]] = None) -> Dict:
        """
        收集新闻数据
        
        Args:
            target: 目标公司或主题
            timeframe: 时间范围，如 "1d", "1w", "1m"
            fields: 需要收集的字段列表，如 ["title", "content", "source", "publish_time", "sentiment"]
            
        Returns:
            新闻数据
        """
        self.logger.info(f"Collecting news data for {target} with timeframe={timeframe}, fields={fields}")
        
        # 使用第一个可用的数据源
        for source_name, source in self.sources.items():
            self.logger.info(f"Trying source: {source_name}")
            if source.is_available():
                self.logger.info(f"Source {source_name} is available, attempting to get data")
                try:
                    data = source.get_data(target, timeframe or "1d", fields or ["title", "content", "source", "publish_time", "sentiment"])
                    self.logger.info(f"Successfully got data from {source_name}")
                    if self.validate(data):
                        self.logger.info(f"Data from {source_name} passed validation")
                        return data
                    else:
                        self.logger.warning(f"Data from {source_name} failed validation")
                except Exception as e:
                    self.logger.error(f"Error collecting data from {source_name}: {str(e)}", exc_info=True)
                    continue
            else:
                self.logger.warning(f"Source {source_name} is not available")
        
        self.logger.error("No available data source found after trying all sources")
        raise ValueError("No available data source")