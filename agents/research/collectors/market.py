from typing import Dict, List, Optional, Any
from .base import BaseCollector, DataSource
import asyncio
import json
import logging
from .mcp.market_tools import (
    fetch_wind_data,
    fetch_tushare_data,
    validate_market_data
)

class WindDataSource(DataSource):
    """Wind数据源"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config.get('api_key')
        self.connected = True
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"Initializing WindDataSource with config: {config}")
    
    def get_name(self) -> str:
        return "wind"
    
    def is_available(self) -> bool:
        available = self.connected
        self.logger.info(f"WindDataSource availability check: {available}")
        return available
    
    def get_data(self, target: str, timeframe: str, fields: List[str]) -> Dict:
        self.logger.info(f"Fetching data from Wind for target={target}, timeframe={timeframe}, fields={fields}")
        # 创建事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # 获取数据
            self.logger.info("Calling fetch_wind_data")
            raw_data = loop.run_until_complete(fetch_wind_data(target, timeframe, fields))
            self.logger.info("Successfully got raw data from fetch_wind_data")
            data = json.loads(raw_data)
            
            # 验证数据
            self.logger.info("Validating market data")
            validation_result = loop.run_until_complete(validate_market_data(json.dumps(data)))
            validation_data = json.loads(validation_result)
            if not validation_data["valid"]:
                self.logger.error(f"Market data validation failed: {validation_data}")
                raise ValueError("Market data validation failed")
            
            self.logger.info("Data validation successful")
            return data
        except Exception as e:
            self.logger.error(f"Error in get_data: {str(e)}", exc_info=True)
            raise
        finally:
            loop.close()
    
    def get_metadata(self) -> Dict:
        return {
            "supported_fields": ["open", "close", "high", "low", "volume"],
            "supported_timeframes": ["1d", "1w", "1m", "1y"],
            "rate_limit": 100
        }

class TushareDataSource(DataSource):
    """Tushare数据源"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.token = config.get('token')
        self.connected = True  # 改为默认可用
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"Initializing TushareDataSource with config: {config}")
    
    def get_name(self) -> str:
        return "tushare"
    
    def is_available(self) -> bool:
        available = self.connected
        self.logger.info(f"TushareDataSource availability check: {available}")
        return available
    
    def get_data(self, target: str, timeframe: str, fields: List[str]) -> Dict:
        self.logger.info(f"Fetching data from Tushare for target={target}, timeframe={timeframe}, fields={fields}")
        # 创建事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # 获取数据
            self.logger.info("Calling fetch_tushare_data")
            raw_data = loop.run_until_complete(fetch_tushare_data(target, timeframe, fields))
            self.logger.info("Successfully got raw data from fetch_tushare_data")
            data = json.loads(raw_data)
            
            # 验证数据
            self.logger.info("Validating market data")
            validation_result = loop.run_until_complete(validate_market_data(json.dumps(data)))
            validation_data = json.loads(validation_result)
            if not validation_data["valid"]:
                self.logger.error(f"Market data validation failed: {validation_data}")
                raise ValueError("Market data validation failed")
            
            self.logger.info("Data validation successful")
            return data
        except Exception as e:
            self.logger.error(f"Error in get_data: {str(e)}", exc_info=True)
            raise
        finally:
            loop.close()
    
    def get_metadata(self) -> Dict:
        return {
            "supported_fields": ["open", "close", "high", "low", "volume"],
            "supported_timeframes": ["1d", "1w", "1m", "1y"],
            "rate_limit": 200
        }

class MarketDataCollector(BaseCollector):
    """市场数据采集器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初始化市场数据采集器
        
        Args:
            config: 配置信息，如果为None或为空则使用默认配置
        """
        # 初始化 logger
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 如果配置为空或None，使用默认配置
        if not config:
            config = {
                'sources': {
                    'wind': {'api_key': 'default'},
                    'tushare': {'token': 'default'}
                }
            }
            self.logger.info("Using default configuration")
        
        self.logger.info(f"Initializing MarketDataCollector with config: {config}")
        super().__init__(config)
    
    def _setup_sources(self) -> None:
        """初始化数据源"""
        # 从配置中加载数据源
        sources_config = self.config.get('sources', {})
        self.logger.info(f"Setting up market sources with config: {sources_config}")
        
        # 添加Wind数据源
        if 'wind' in sources_config:
            self.logger.info("Initializing Wind source")
            wind_source = WindDataSource(sources_config['wind'])
            self.register_source(wind_source)
            self.logger.info(f"Wind source initialized and registered. Available: {wind_source.is_available()}")
        
        # 添加Tushare数据源
        if 'tushare' in sources_config:
            self.logger.info("Initializing Tushare source")
            tushare_source = TushareDataSource(sources_config['tushare'])
            self.register_source(tushare_source)
            self.logger.info(f"Tushare source initialized and registered. Available: {tushare_source.is_available()}")
        
        self.logger.info(f"Total registered sources: {len(self.sources)}")
        for name, source in self.sources.items():
            self.logger.info(f"Source {name} available: {source.is_available()}")
    
    def validate(self, data: Dict) -> bool:
        """验证数据格式"""
        # 创建事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # 验证数据
            validation_result = loop.run_until_complete(validate_market_data(json.dumps(data)))
            return json.loads(validation_result)["valid"]
        finally:
            loop.close()
    
    def collect(self, target: str, timeframe: Optional[str] = None, fields: Optional[List[str]] = None) -> Dict:
        """
        收集市场数据
        
        Args:
            target: 股票代码
            timeframe: 时间范围，如 "1d", "1w", "1m", "1y"
            fields: 需要收集的字段列表，如 ["open", "close", "high", "low", "volume"]
            
        Returns:
            市场数据
        """
        self.logger.info(f"Collecting market data for {target} with timeframe={timeframe}, fields={fields}")
        
        # 使用第一个可用的数据源
        for source_name, source in self.sources.items():
            self.logger.info(f"Trying source: {source_name}")
            if source.is_available():
                self.logger.info(f"Source {source_name} is available, attempting to get data")
                try:
                    data = source.get_data(target, timeframe or "1d", fields or ["open", "close", "high", "low", "volume"])
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