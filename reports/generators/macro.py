from typing import Dict, Any
from .base import BaseReportGenerator

class MacroReportGenerator(BaseReportGenerator):
    """宏观研报生成器"""
    
    def generate(self, data: Dict[str, Any], target: str) -> str:
        """
        生成宏观研报
        
        Args:
            data: 报告数据，包含 news_data
            target: 宏观主题
            
        Returns:
            报告文件路径
        """
        news_data = data["news_data"]
        
        # 生成报告内容
        content = f"""# {target} 宏观研究报告

## 1. 主题概述

### 1.1 研究背景
本报告针对{target}主题进行深入分析，重点关注相关政策、市场动态和发展趋势。

## 2. 相关动态

### 2.1 重要新闻
"""
        
        # 添加新闻内容
        for news in news_data["news"]:
            content += f"""
#### {news['title']}
- 来源：{news['source']}
- 发布时间：{news['publish_time']}
- 情感倾向：{news['sentiment']}
- 内容：{news['content']}
"""
        
        # 保存报告
        return self._save_report(content, target, "macro") 