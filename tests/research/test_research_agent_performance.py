import unittest
import time
import statistics
from typing import Dict, List, Callable
from agents.research.agent import ResearchAgent
from agents.base import BaseAgent, MessageType, AgentState

class TestResearchAgentPerformance(unittest.TestCase):
    """ResearchAgent性能测试"""
    
    def setUp(self):
        """测试前准备"""
        self.research_agent = ResearchAgent()
        self.iterations = 100  # 每个测试的迭代次数
    
    def _measure_execution_time(self, func, *args, **kwargs) -> float:
        """测量函数执行时间"""
        start_time = time.time()
        func(*args, **kwargs)
        end_time = time.time()
        return end_time - start_time
    
    def _run_performance_test(self, func: Callable, *args, iterations: int = 100) -> Dict[str, float]:
        """运行性能测试
        
        Args:
            func: 要测试的函数
            *args: 函数参数
            iterations: 迭代次数
            
        Returns:
            性能统计信息
        """
        times = []
        for _ in range(iterations):
            start_time = time.time()
            func(*args)
            end_time = time.time()
            times.append(end_time - start_time)
        
        return {
            "avg_time": sum(times) / len(times),
            "max_time": max(times),
            "min_time": min(times),
            "std_dev": statistics.stdev(times) if len(times) > 1 else 0
        }
    
    def test_market_data_collection_performance(self):
        """测试市场数据收集性能"""
        task = {
            "type": "market",
            "target": "000001",
            "timeframe": "1d",
            "fields": ["open", "close", "high", "low", "volume"]
        }
        
        stats = self._run_performance_test(self.research_agent.execute, task)
        
        # 验证性能指标
        self.assertLess(stats["avg_time"], 1.0)  # 平均执行时间应小于1秒
        self.assertLess(stats["max_time"], 2.0)   # 最大执行时间应小于2秒
        self.assertLess(stats["std_dev"], 0.5)  # 标准差应小于0.5秒
    
    def test_financial_data_collection_performance(self):
        """测试财务数据收集性能"""
        task = {
            "type": "financial",
            "target": "000001",
            "timeframe": "2023Q1",
            "fields": ["revenue", "profit", "assets", "liabilities", "equity"]
        }
        
        stats = self._run_performance_test(self.research_agent.execute, task)
        
        # 验证性能指标
        self.assertLess(stats["avg_time"], 1.0)
        self.assertLess(stats["max_time"], 2.0)
        self.assertLess(stats["std_dev"], 0.5)
    
    def test_news_data_collection_performance(self):
        """测试新闻数据收集性能"""
        task = {
            "type": "news",
            "target": "000001",
            "timeframe": "1d",
            "fields": ["title", "content", "source", "url", "publish_time", "sentiment"]
        }
        
        stats = self._run_performance_test(self.research_agent.execute, task)
        
        # 验证性能指标
        self.assertLess(stats["avg_time"], 1.0)
        self.assertLess(stats["max_time"], 2.0)
        self.assertLess(stats["std_dev"], 0.5)
    
    def test_concurrent_data_collection_performance(self):
        """测试并发数据收集性能"""
        tasks = [
            {
                "type": "market",
                "target": "000001",
                "timeframe": "1d"
            },
            {
                "type": "financial",
                "target": "000001",
                "timeframe": "2023Q1"
            },
            {
                "type": "news",
                "target": "000001",
                "timeframe": "1d"
            }
        ]
        
        def concurrent_test():
            for task in tasks:
                self.research_agent.execute(task)
        
        stats = self._run_performance_test(concurrent_test)
        
        # 验证性能指标
        self.assertLess(stats["avg_time"], 3.0)  # 并发执行时间应小于3秒
        self.assertLess(stats["max_time"], 5.0)   # 最大执行时间应小于5秒
        self.assertLess(stats["std_dev"], 1.0)  # 标准差应小于1秒
    
    def test_memory_usage(self):
        """测试内存使用情况"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # 执行一系列任务
        for _ in range(100):
            task = {
                "type": "market",
                "target": "000001",
                "timeframe": "1d"
            }
            self.research_agent.execute(task)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # 验证内存使用
        self.assertLess(memory_increase, 100 * 1024 * 1024)  # 内存增加应小于100MB
    
    def test_error_handling_performance(self):
        """测试错误处理性能"""
        task = {
            "type": "invalid",
            "target": "000001"
        }
        
        stats = self._run_performance_test(
            lambda: self.assertRaises(ValueError, self.research_agent.execute, task)
        )
        
        # 验证性能指标
        self.assertLess(stats["avg_time"], 0.1)  # 错误处理应非常快
        self.assertLess(stats["max_time"], 0.2)
        self.assertLess(stats["std_dev"], 0.05)
    
    def test_message_handling_performance(self):
        """测试消息处理性能"""
        class MockMessage:
            def __init__(self, sender, content, type=MessageType.REQUEST):
                self.sender = sender
                self.content = content
                self.type = type
        
        message = MockMessage(
            "test_sender",
            {
                "action": "get_data",
                "task": {
                    "type": "market",
                    "target": "000001",
                    "timeframe": "1d"
                }
            }
        )
        
        stats = self._run_performance_test(self.research_agent.handle_message, message)
        
        # 验证性能指标
        self.assertLess(stats["avg_time"], 1.0)
        self.assertLess(stats["max_time"], 2.0)
        self.assertLess(stats["std_dev"], 0.5)
    
    def test_cleanup_performance(self):
        """测试清理性能"""
        stats = self._run_performance_test(self.research_agent.cleanup)
        
        # 验证性能指标
        self.assertLess(stats["avg_time"], 0.1)  # 清理应非常快
        self.assertLess(stats["max_time"], 0.2)
        self.assertLess(stats["std_dev"], 0.05)
    
    def tearDown(self):
        """测试后清理"""
        self.research_agent.cleanup()

if __name__ == '__main__':
    unittest.main() 