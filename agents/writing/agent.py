import logging
from typing import Dict, Any
from agents.base import BaseAgent, AgentState
from utils.openai_client import OpenAIClient

class WritingAgent(BaseAgent):
    """写作代理"""
    
    def __init__(self, name: str = "WritingAgent", config: Dict[str, Any] = None):
        """初始化写作代理
        
        Args:
            name: 代理名称
            config: 配置信息
        """
        super().__init__(name, config)
        self.openai_client = OpenAIClient()
        self.logger = logging.getLogger(__name__)
    
    def execute(self, data: Dict[str, Any]) -> str:
        """执行写作任务
        
        Args:
            data: 包含以下字段的字典：
                - type: 报告类型（company/industry/macro）
                - target: 目标（公司/行业/主题）
                - analysis_results: 分析结果
                
        Returns:
            str: 报告内容
        """
        try:
            self.logger.info(f"开始生成{data['type']}报告...")
            
            # 生成报告
            report = self.openai_client.write_report(
                data['type'],
                data['target'],
                data['analysis_results']
            )
            
            self.logger.info(f"{data['type']}报告生成完成")
            return report
            
        except Exception as e:
            self.logger.error(f"生成报告失败: {str(e)}")
            raise
    
    def _validate_data(self, data: Dict[str, Any]):
        """验证数据格式"""
        required_fields = ["type", "target", "analysis_results"]
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
        self.logger.info("清理写作代理资源")
        self.state = AgentState.IDLE 