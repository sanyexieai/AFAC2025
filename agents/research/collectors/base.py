from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import logging

class BaseCollector(ABC):
    """数据采集器基类"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self._setup_logger()
    
    def _setup_logger(self) -> None:
        """设置日志记录器"""
        self.logger = logging.getLogger(self.__class__.__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    @abstractmethod
    def collect(self, target: str, timeframe: Optional[str] = None, fields: Optional[List[str]] = None) -> Dict:
        """
        收集数据
        
        Args:
            target: 目标对象（如股票代码、公司名称等）
            timeframe: 时间范围
            fields: 需要收集的字段列表
            
        Returns:
            收集到的数据
        """
        pass
    
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