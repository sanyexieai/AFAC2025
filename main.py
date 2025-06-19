#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import os
from typing import Dict, Any
from agents.orchestrator import Orchestrator
from reports.generators.company import CompanyReportGenerator
from reports.generators.industry import IndustryReportGenerator
from reports.generators.macro import MacroReportGenerator

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="生成研究报告")
    parser.add_argument("--type", required=True, choices=["company", "industry", "macro"],
                      help="报告类型：company（公司）、industry（行业）、macro（宏观）")
    parser.add_argument("--target", required=True,
                      help="目标：公司代码、行业名称或宏观主题")
    parser.add_argument("--timeframe", required=False,
                      help="时间范围：如 2023Q1、2023H1、2023Y")
    parser.add_argument("--output", default="reports",
                      help="输出目录，默认为 reports")
    return parser.parse_args()

def setup_logging():
    """配置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

def generate_report(report_type: str, target: str, timeframe: str, output_dir: str) -> Dict[str, Any]:
    """生成报告
    
    Args:
        report_type: 报告类型（company/industry/macro）
        target: 目标（公司/行业/主题）
        timeframe: 时间范围
        output_dir: 输出目录
        
    Returns:
        Dict[str, Any]: 报告生成结果
    """
    logger = logging.getLogger(__name__)
    
    try:
        # 创建协调器
        orchestrator = Orchestrator()
        
        # 生成报告
        result = orchestrator.generate_report(report_type, target, timeframe)
        
        # 保存报告
        os.makedirs(output_dir, exist_ok=True)
        report_path = os.path.join(output_dir, f"{target}_{timeframe}_{report_type}.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(result["report"])
        
        logger.info(f"报告已保存到：{report_path}")
        
        # 清理资源
        orchestrator.cleanup()
        
        return result
        
    except Exception as e:
        logger.error(f"生成报告失败: {str(e)}")
        raise

def main():
    """主函数"""
    # 解析命令行参数
    args = parse_args()
    
    # 配置日志
    setup_logging()
    
    # 生成报告
    generate_report(args.type, args.target, args.timeframe, args.output)

if __name__ == "__main__":
    main() 