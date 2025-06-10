import logging
from typing import Dict, Any
from agents.base import BaseAgent, AgentState
from utils.openai_client import OpenAIClient

class AnalysisAgent(BaseAgent):
    """分析代理，负责分析收集到的数据"""
    
    def __init__(self, name: str = "AnalysisAgent", config: Dict[str, Any] = None):
        """初始化分析代理
        
        Args:
            name: 代理名称
            config: 配置信息
        """
        super().__init__(name, config)
        self.openai_client = OpenAIClient()
        self.logger = logging.getLogger(__name__)
    
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """执行数据分析
        
        Args:
            data: 包含以下字段的字典：
                - type: 报告类型（company/industry/macro）
                - target: 目标（公司/行业/主题）
                - timeframe: 时间范围
                - data: 要分析的数据
                
        Returns:
            Dict[str, Any]: 分析结果
        """
        try:
            self.logger.info(f"开始分析{data['type']}数据...")
            
            # 验证数据
            self._validate_data(data)
            
            # 根据报告类型分析数据
            if data["type"] == "company":
                result = self._analyze_company_data(data)
            elif data["type"] == "industry":
                result = self._analyze_industry_data(data)
            else:  # macro
                result = self._analyze_macro_data(data)
            
            self.logger.info(f"{data['type']}数据分析完成")
            return result
            
        except Exception as e:
            self.logger.error(f"数据分析失败: {str(e)}")
            raise
    
    def _validate_data(self, data: Dict[str, Any]):
        """验证数据格式"""
        required_fields = ["type", "target", "timeframe", "data"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"缺少必要字段：{field}")
        
        if data["type"] not in ["company", "industry", "macro"]:
            raise ValueError(f"不支持的报告类型：{data['type']}")
    
    def _analyze_company_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """分析公司数据
        
        Args:
            data: 包含公司数据的字典
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        # 分析市场数据
        market_analysis = self.openai_client.analyze(
            "market",
            data["data"]["market_data"]
        )
        
        # 分析财务数据
        financial_analysis = self.openai_client.analyze(
            "financial",
            data["data"]["financial_data"]
        )
        
        # 分析新闻数据
        news_analysis = self.openai_client.analyze(
            "news",
            data["data"]["news_data"]
        )
        
        return {
            "market_analysis": market_analysis,
            "financial_analysis": financial_analysis,
            "news_analysis": news_analysis
        }
    
    def _analyze_industry_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """分析行业数据
        
        Args:
            data: 包含行业数据的字典
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        # 分析市场数据
        market_analysis = self.openai_client.analyze(
            "market",
            data["data"]["market_data"]
        )
        
        # 分析新闻数据
        news_analysis = self.openai_client.analyze(
            "news",
            data["data"]["news_data"]
        )
        
        return {
            "market_analysis": market_analysis,
            "news_analysis": news_analysis
        }
    
    def _analyze_macro_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """分析宏观数据
        
        Args:
            data: 包含宏观数据的字典
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        # 分析新闻数据
        news_analysis = self.openai_client.analyze(
            "news",
            data["data"]["news_data"]
        )
        
        return {
            "news_analysis": news_analysis
        }
    
    def _validate_impl(self, data: Dict[str, Any]) -> bool:
        """
        实现基类的抽象方法，验证数据格式
        
        Args:
            data: 要验证的数据
            
        Returns:
            验证是否通过
        """
        try:
            self._validate_data(data)
            return True
        except ValueError:
            return False
    
    def cleanup(self) -> None:
        """清理资源"""
        self.logger.info("清理分析代理资源")
        self.state = AgentState.IDLE 