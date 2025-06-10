from typing import Any, Dict, List, Optional
import logging

class DataValidator:
    """数据验证器，负责验证收集到的数据"""
    
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
    
    def validate(self, data: Dict) -> bool:
        """
        验证数据
        
        Args:
            data: 待验证的数据
            
        Returns:
            验证是否通过
        """
        try:
            # 检查数据完整性
            if not self._check_completeness(data):
                self.logger.error("Data completeness check failed")
                return False
            
            # 检查数据一致性
            if not self._check_consistency(data):
                self.logger.error("Data consistency check failed")
                return False
            
            # 检查数据有效性
            if not self._check_validity(data):
                self.logger.error("Data validity check failed")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Validation error: {str(e)}")
            return False
    
    def _check_completeness(self, data: Dict) -> bool:
        """
        检查数据完整性
        
        Args:
            data: 待验证的数据
            
        Returns:
            检查是否通过
        """
        # 检查必要字段
        if not isinstance(data, dict):
            return False
        
        # 根据数据类型检查必要字段
        if "type" in data:
            if data["type"] == "market":
                required_fields = ["code", "timeframe", "data"]
            elif data["type"] == "financial":
                required_fields = ["company", "period", "data"]
            elif data["type"] == "news":
                required_fields = ["target", "timeframe", "news"]
            else:
                return False
            
            return all(field in data for field in required_fields)
        
        return True
    
    def _check_consistency(self, data: Dict) -> bool:
        """
        检查数据一致性
        
        Args:
            data: 待验证的数据
            
        Returns:
            检查是否通过
        """
        # 检查数据类型一致性
        if "type" in data:
            if data["type"] == "market":
                return self._check_market_consistency(data)
            elif data["type"] == "financial":
                return self._check_financial_consistency(data)
            elif data["type"] == "news":
                return self._check_news_consistency(data)
        
        return True
    
    def _check_validity(self, data: Dict) -> bool:
        """
        检查数据有效性
        
        Args:
            data: 待验证的数据
            
        Returns:
            检查是否通过
        """
        # 检查数据类型有效性
        if "type" in data:
            if data["type"] == "market":
                return self._check_market_validity(data)
            elif data["type"] == "financial":
                return self._check_financial_validity(data)
            elif data["type"] == "news":
                return self._check_news_validity(data)
        
        return True
    
    def _check_market_consistency(self, data: Dict) -> bool:
        """检查市场数据一致性"""
        if not isinstance(data["data"], dict):
            return False
        
        # 检查价格一致性
        if all(key in data["data"] for key in ["open", "close", "high", "low"]):
            prices = [
                data["data"]["open"],
                data["data"]["close"],
                data["data"]["high"],
                data["data"]["low"]
            ]
            if min(prices) != data["data"]["low"] or max(prices) != data["data"]["high"]:
                return False
        
        return True
    
    def _check_financial_consistency(self, data: Dict) -> bool:
        """检查财务数据一致性"""
        if not isinstance(data["data"], dict):
            return False
        
        # 检查资产负债表一致性
        if all(key in data["data"] for key in ["assets", "liabilities", "equity"]):
            if data["data"]["assets"] != data["data"]["liabilities"] + data["data"]["equity"]:
                return False
        
        return True
    
    def _check_news_consistency(self, data: Dict) -> bool:
        """检查新闻数据一致性"""
        if not isinstance(data["news"], list):
            return False
        
        # 检查新闻列表一致性
        for news in data["news"]:
            if not isinstance(news, dict):
                return False
            if not all(key in news for key in ["title", "content", "source", "url", "publish_time", "sentiment"]):
                return False
        
        return True
    
    def _check_market_validity(self, data: Dict) -> bool:
        """检查市场数据有效性"""
        if not isinstance(data["data"], dict):
            return False
        
        # 检查数值有效性
        for key in ["open", "close", "high", "low", "volume"]:
            if key in data["data"]:
                if not isinstance(data["data"][key], (int, float)):
                    return False
                if data["data"][key] < 0:
                    return False
        
        return True
    
    def _check_financial_validity(self, data: Dict) -> bool:
        """检查财务数据有效性"""
        if not isinstance(data["data"], dict):
            return False
        
        # 检查数值有效性
        for key in ["revenue", "profit", "assets", "liabilities", "equity"]:
            if key in data["data"]:
                if not isinstance(data["data"][key], (int, float)):
                    return False
        
        return True
    
    def _check_news_validity(self, data: Dict) -> bool:
        """检查新闻数据有效性"""
        if not isinstance(data["news"], list):
            return False
        
        # 检查新闻有效性
        for news in data["news"]:
            if not isinstance(news, dict):
                return False
            
            # 检查情感值范围
            if "sentiment" in news:
                if not isinstance(news["sentiment"], (int, float)):
                    return False
                if not 0 <= news["sentiment"] <= 1:
                    return False
        
        return True 