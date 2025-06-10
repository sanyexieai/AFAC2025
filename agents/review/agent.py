from typing import Dict, Any, List, Optional
import logging
from agents.base import BaseAgent, AgentState, MessageType
from utils.openai_client import OpenAIClient

class ReviewAgent(BaseAgent):
    """审核代理"""
    
    def __init__(self, name: str = "ReviewAgent", config: Dict[str, Any] = None):
        """初始化审核代理
        
        Args:
            name: 代理名称
            config: 配置信息
        """
        super().__init__(name, config)
        self.openai_client = OpenAIClient()
        self.logger = logging.getLogger(__name__)
    
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """执行审核任务
        
        Args:
            data: 包含以下字段的字典：
                - type: 报告类型（company/industry/macro）
                - target: 目标（公司/行业/主题）
                - content: 报告内容
                - analysis_results: 分析结果
                
        Returns:
            Dict[str, Any]: 审核结果
        """
        try:
            self.logger.info(f"开始审核{data['type']}报告...")
            
            # 审核报告
            result = self.openai_client.review_report(
                data['type'],
                data['target'],
                data['content'],
                data['analysis_results']
            )
            
            self.logger.info(f"{data['type']}报告审核完成")
            return result
            
        except Exception as e:
            self.logger.error(f"审核报告失败: {str(e)}")
            raise
    
    def _validate_data(self, data: Dict[str, Any]):
        """验证数据格式"""
        required_fields = ["type", "target", "content", "analysis_results"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"缺少必要字段：{field}")
        
        if data["type"] not in ["company", "industry", "macro"]:
            raise ValueError(f"不支持的报告类型：{data['type']}")
    
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
        self.logger.info("清理审核智能体资源")
        self.state = AgentState.IDLE 