from abc import ABC, abstractmethod
from typing import Dict, Any
import os
import json
from datetime import datetime

class BaseReportGenerator(ABC):
    """报告生成器基类"""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        self._ensure_output_dir()
    
    def _ensure_output_dir(self) -> None:
        """确保输出目录存在"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    @abstractmethod
    def generate(self, data: Dict[str, Any], target: str) -> str:
        """
        生成报告
        
        Args:
            data: 报告数据
            target: 目标对象
            
        Returns:
            报告文件路径
        """
        pass
    
    def _save_report(self, content: str, target: str, report_type: str) -> str:
        """
        保存报告
        
        Args:
            content: 报告内容
            target: 目标对象
            report_type: 报告类型
            
        Returns:
            报告文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{report_type}_{target}_{timestamp}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        return filepath 