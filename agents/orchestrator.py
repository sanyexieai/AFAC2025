import logging
from typing import Dict, Any
from agents.research.agent import ResearchAgent
from agents.analysis.agent import AnalysisAgent
from agents.writing.agent import WritingAgent
from agents.review.agent import ReviewAgent

class Orchestrator:
    """协调器，负责协调各个代理的工作"""
    
    def __init__(self):
        """初始化协调器"""
        self.logger = logging.getLogger(__name__)
        
        # 初始化各个代理
        self.research_agent = ResearchAgent(name="ResearchAgent")
        self.analysis_agent = AnalysisAgent(name="AnalysisAgent")
        self.writing_agent = WritingAgent(name="WritingAgent")
        self.review_agent = ReviewAgent(name="ReviewAgent")
        
        self.logger.info("协调器初始化完成")
    
    def generate_report(self, report_type: str, target: str, timeframe: str) -> Dict[str, Any]:
        """生成报告
        
        Args:
            report_type: 报告类型（company/industry/macro）
            target: 目标（公司/行业/主题）
            timeframe: 时间范围
            
        Returns:
            Dict[str, Any]: 报告生成结果
        """
        try:
            self.logger.info(f"开始生成{report_type}报告...")
            
            # 1. 收集数据
            research_data = self.research_agent.execute({
                "type": report_type,
                "target": target,
                "timeframe": timeframe
            })
            
            # 2. 分析数据
            analysis_results = self.analysis_agent.execute({
                "type": report_type,
                "target": target,
                "timeframe": timeframe,
                "data": research_data
            })
            
            # 3. 生成报告
            report = self.writing_agent.execute({
                "type": report_type,
                "target": target,
                "timeframe": timeframe,
                "analysis_results": analysis_results
            })
            
            # 4. 审核报告
            review_result = self.review_agent.execute({
                "type": report_type,
                "target": target,
                "timeframe": timeframe,
                "content": report,
                "analysis_results": analysis_results
            })
            
            self.logger.info(f"{report_type}报告生成完成")
            return {
                "report": report,
                "review": review_result
            }
            
        except Exception as e:
            self.logger.error(f"生成报告失败: {str(e)}")
            raise
    
    def cleanup(self):
        """清理资源"""
        self.logger.info("清理协调器资源...")
        
        # 清理各个代理的资源
        self.research_agent.cleanup()
        self.analysis_agent.cleanup()
        self.writing_agent.cleanup()
        self.review_agent.cleanup()
        
        self.logger.info("协调器资源清理完成") 