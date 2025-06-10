from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import logging
import time
from datetime import datetime

class DataSource(ABC):
    """数据源接口基类"""
    
    @abstractmethod
    def get_name(self) -> str:
        """获取数据源名称"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查数据源是否可用"""
        pass
    
    @abstractmethod
    def get_data(self, target: str, timeframe: str, fields: List[str]) -> Dict:
        """获取数据"""
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict:
        """获取数据源元数据"""
        pass

class BaseCollector:
    """数据采集器基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sources: Dict[str, DataSource] = {}
        self._setup_sources()
        self._setup_cache()
    
    def _setup_sources(self) -> None:
        """初始化数据源"""
        pass
    
    def _setup_cache(self) -> None:
        """初始化缓存"""
        self.cache = {}
        self.cache_ttl = self.config.get('cache_ttl', 3600)  # 默认缓存1小时
    
    def _get_from_cache(self, key: str) -> Optional[Dict]:
        """从缓存获取数据"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return data
        return None
    
    def _save_to_cache(self, key: str, data: Dict) -> None:
        """保存数据到缓存"""
        self.cache[key] = (data, time.time())
    
    def register_source(self, source: DataSource) -> None:
        """注册数据源"""
        self.sources[source.get_name()] = source
    
    def unregister_source(self, name: str) -> None:
        """注销数据源"""
        if name in self.sources:
            del self.sources[name]
    
    def get_available_sources(self) -> List[str]:
        """获取可用的数据源"""
        return [
            name for name, source in self.sources.items()
            if source.is_available()
        ]
    
    def collect(self, target: str, timeframe: str, fields: List[str]) -> Dict:
        """数据采集主方法"""
        # 1. 检查缓存
        cache_key = f"{target}_{timeframe}_{','.join(fields)}"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        # 2. 获取数据
        for source_name in self.get_available_sources():
            try:
                source = self.sources[source_name]
                data = source.get_data(target, timeframe, fields)
                
                # 3. 保存到缓存
                self._save_to_cache(cache_key, data)
                return data
                
            except Exception as e:
                self.logger.error(f"从{source_name}获取数据失败: {str(e)}")
                continue
        
        raise ValueError("没有可用的数据源")
    
    def validate(self, data: Dict) -> bool:
        """
        验证数据
        
        Args:
            data: 待验证的数据
            
        Returns:
            验证是否通过
        """
        try:
            return self._validate_impl(data)
        except Exception as e:
            self.logger.error(f"Validation error: {str(e)}")
            return False
    
    @abstractmethod
    def _validate_impl(self, data: Dict) -> bool:
        """
        实现具体的验证逻辑
        
        Args:
            data: 待验证的数据
            
        Returns:
            验证是否通过
        """
        pass
    
    def cleanup(self) -> None:
        """清理资源"""
        self.logger.info("Cleaning up resources") 