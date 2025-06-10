#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
from typing import Dict, Optional
from agents.research.agent import ResearchAgent
from agents.base import MessageType, AgentState

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='智能金融研报生成系统')
    parser.add_argument('--type', type=str, required=True, choices=['company', 'industry', 'macro'],
                      help='研报类型：company(公司研报)、industry(行业研报)、macro(宏观研报)')
    parser.add_argument('--target', type=str, required=True,
                      help='目标对象：公司代码/行业名称/宏观主题')
    parser.add_argument('--timeframe', type=str, default='1d',
                      help='时间范围，默认1d')
    parser.add_argument('--output', type=str, default='reports',
                      help='输出目录，默认reports')
    return parser.parse_args()

def generate_report(report_type: str, target: str, timeframe: str = '1d', output_dir: str = 'reports') -> None:
    """
    生成研报
    
    Args:
        report_type: 研报类型
        target: 目标对象
        timeframe: 时间范围
        output_dir: 输出目录
    """
    logger.info(f"开始生成{report_type}类型研报，目标：{target}")
    
    # 创建研究代理
    research_agent = ResearchAgent()
    
    try:
        # 根据研报类型收集数据
        if report_type == 'company':
            # 收集公司数据
            market_data = research_agent.execute({
                "type": "market",
                "target": target,
                "timeframe": timeframe,
                "fields": ["open", "close", "high", "low", "volume"]
            })
            
            financial_data = research_agent.execute({
                "type": "financial",
                "target": target,
                "timeframe": timeframe,
                "fields": ["revenue", "profit", "assets", "liabilities", "equity"]
            })
            
            news_data = research_agent.execute({
                "type": "news",
                "target": target,
                "timeframe": timeframe,
                "fields": ["title", "content", "source", "sentiment"]
            })
            
            logger.info("公司数据收集完成")
            
        elif report_type == 'industry':
            # 收集行业数据
            market_data = research_agent.execute({
                "type": "market",
                "target": target,
                "timeframe": timeframe,
                "fields": ["index", "change", "volume"]
            })
            
            news_data = research_agent.execute({
                "type": "news",
                "target": target,
                "timeframe": timeframe,
                "fields": ["title", "content", "source", "sentiment"]
            })
            
            logger.info("行业数据收集完成")
            
        elif report_type == 'macro':
            # 收集宏观数据
            news_data = research_agent.execute({
                "type": "news",
                "target": target,
                "timeframe": timeframe,
                "fields": ["title", "content", "source", "sentiment"]
            })
            
            logger.info("宏观数据收集完成")
        
        # TODO: 实现报告生成逻辑
        logger.info(f"研报生成完成，输出目录：{output_dir}")
        
    except Exception as e:
        logger.error(f"研报生成失败：{str(e)}")
        raise
    finally:
        # 清理资源
        research_agent.cleanup()

def main():
    """主函数"""
    args = parse_args()
    generate_report(args.type, args.target, args.timeframe, args.output)

if __name__ == '__main__':
    main() 