import unittest
from typing import Dict, List
from agents.research.agent import ResearchAgent
from agents.base import AgentState, MessageType

class TestResearchAgent(unittest.TestCase):
    """ResearchAgent测试"""
    
    def setUp(self):
        """测试前准备"""
        print("\n=== 开始测试 ResearchAgent ===")
        self.agent = ResearchAgent()
    
    def test_execute_market_data(self):
        """测试市场数据收集任务"""
        print("\n测试市场数据收集...")
        task = {
            "type": "market",
            "target": "000001",
            "timeframe": "1d",
            "fields": ["open", "close", "high", "low", "volume"]
        }
        
        print(f"执行任务: {task}")
        result = self.agent.execute(task)
        print(f"获取结果: {result}")
        
        # 验证返回数据结构
        self.assertIsInstance(result, dict)
        self.assertEqual(result["code"], "000001")
        self.assertEqual(result["timeframe"], "1d")
        self.assertIn("data", result)
        
        # 验证数据字段
        market_data = result["data"]
        self.assertIn("open", market_data)
        self.assertIn("close", market_data)
        self.assertIn("high", market_data)
        self.assertIn("low", market_data)
        self.assertIn("volume", market_data)
        print("市场数据收集测试通过！")
    
    def test_execute_financial_data(self):
        """测试财务数据收集任务"""
        print("\n测试财务数据收集...")
        task = {
            "type": "financial",
            "target": "000001",
            "timeframe": "2023Q1",
            "fields": ["revenue", "profit", "assets", "liabilities", "equity"]
        }
        
        print(f"执行任务: {task}")
        result = self.agent.execute(task)
        print(f"获取结果: {result}")
        
        # 验证返回数据结构
        self.assertIsInstance(result, dict)
        self.assertEqual(result["company"], "000001")
        self.assertEqual(result["period"], "2023Q1")
        self.assertIn("data", result)
        
        # 验证数据字段
        financial_data = result["data"]
        self.assertIn("revenue", financial_data)
        self.assertIn("profit", financial_data)
        self.assertIn("assets", financial_data)
        self.assertIn("liabilities", financial_data)
        self.assertIn("equity", financial_data)
        print("财务数据收集测试通过！")
    
    def test_execute_news_data(self):
        """测试新闻数据收集任务"""
        print("\n测试新闻数据收集...")
        task = {
            "type": "news",
            "target": "000001",
            "timeframe": "1d",
            "fields": ["title", "content", "source", "url", "publish_time", "sentiment"]
        }
        
        print(f"执行任务: {task}")
        result = self.agent.execute(task)
        print(f"获取结果: {result}")
        
        # 验证返回数据结构
        self.assertIsInstance(result, dict)
        self.assertEqual(result["target"], "000001")
        self.assertEqual(result["timeframe"], "1d")
        self.assertIn("news", result)
        
        # 验证新闻列表
        self.assertIsInstance(result["news"], list)
        self.assertGreater(len(result["news"]), 0)
        
        for news in result["news"]:
            self.assertIn("title", news)
            self.assertIn("content", news)
            self.assertIn("source", news)
            self.assertIn("url", news)
            self.assertIn("publish_time", news)
            self.assertIn("sentiment", news)
        print("新闻数据收集测试通过！")
    
    def test_invalid_task(self):
        """测试无效任务"""
        print("\n测试无效任务...")
        # 缺少必要字段
        task1 = {
            "type": "market",
            "timeframe": "1d"
        }
        with self.assertRaises(ValueError):
            self.agent.execute(task1)
        
        # 不支持的数据类型
        task2 = {
            "type": "invalid",
            "target": "000001",
            "timeframe": "1d"
        }
        with self.assertRaises(ValueError):
            self.agent.execute(task2)
        print("无效任务测试通过！")
    
    def test_agent_state(self):
        """测试Agent状态"""
        # 初始状态
        self.assertEqual(self.agent.state, AgentState.IDLE)
        
        # 执行任务
        task = {
            "type": "market",
            "target": "000001",
            "timeframe": "1d"
        }
        self.agent.execute(task)
        
        # 任务完成后的状态
        self.assertEqual(self.agent.state, AgentState.COMPLETED)
    
    def test_handle_task_message(self):
        """测试任务消息处理"""
        class MockMessage:
            def __init__(self, sender, content, type=MessageType.TASK):
                self.sender = sender
                self.content = content
                self.type = type
        
        # 创建测试消息
        message = MockMessage(
            "test_sender",
            {
                "type": "market",
                "target": "000001",
                "timeframe": "1d"
            }
        )
        
        # 处理消息
        self.agent.handle_message(message)
        
        # 验证状态
        self.assertEqual(self.agent.state, AgentState.COMPLETED)
    
    def test_handle_request_message(self):
        """测试请求消息处理"""
        class MockMessage:
            def __init__(self, sender, content, type=MessageType.REQUEST):
                self.sender = sender
                self.content = content
                self.type = type
        
        # 测试获取数据请求
        data_request = MockMessage(
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
        self.agent.handle_message(data_request)
        
        # 测试获取状态请求
        status_request = MockMessage(
            "test_sender",
            {
                "action": "get_status"
            }
        )
        self.agent.handle_message(status_request)
        
        # 测试无效请求
        invalid_request = MockMessage(
            "test_sender",
            {
                "action": "invalid_action"
            }
        )
        with self.assertRaises(ValueError):
            self.agent.handle_message(invalid_request)
    
    def test_handle_command_message(self):
        """测试命令消息处理"""
        class MockMessage:
            def __init__(self, sender, content, type=MessageType.COMMAND):
                self.sender = sender
                self.content = content
                self.type = type
        
        # 测试清理命令
        cleanup_command = MockMessage(
            "test_sender",
            {
                "action": "cleanup"
            }
        )
        self.agent.handle_message(cleanup_command)
        
        # 测试重置命令
        reset_command = MockMessage(
            "test_sender",
            {
                "action": "reset"
            }
        )
        self.agent.handle_message(reset_command)
        
        # 测试无效命令
        invalid_command = MockMessage(
            "test_sender",
            {
                "action": "invalid_action"
            }
        )
        with self.assertRaises(ValueError):
            self.agent.handle_message(invalid_command)
    
    def test_handle_error_message(self):
        """测试错误消息处理"""
        class MockMessage:
            def __init__(self, sender, content, type=MessageType.ERROR):
                self.sender = sender
                self.content = content
                self.type = type
        
        # 创建错误消息
        error_message = MockMessage(
            "test_sender",
            "Test error message"
        )
        
        # 处理错误消息
        self.agent.handle_message(error_message)
        
        # 验证状态
        self.assertEqual(self.agent.state, AgentState.ERROR)
    
    def test_handle_unsupported_message(self):
        """测试不支持的消息类型"""
        class MockMessage:
            def __init__(self, sender, content, type="UNSUPPORTED"):
                self.sender = sender
                self.content = content
                self.type = type
        
        # 创建不支持的消息
        unsupported_message = MockMessage(
            "test_sender",
            "Test message"
        )
        
        # 处理消息
        self.agent.handle_message(unsupported_message)
        # 不应该抛出异常，只记录警告
    
    def test_cleanup(self):
        """测试资源清理"""
        # 创建代理
        agent = ResearchAgent()
        
        # 执行清理
        agent.cleanup()
        
        # 验证状态
        self.assertEqual(agent.state, AgentState.IDLE)
        
        # 验证收集器已清理
        for collector in [agent.market_collector, agent.financial_collector, agent.news_collector]:
            self.assertEqual(len(collector.logger.handlers), 0)
            self.assertIsNone(collector.data)
    
    def tearDown(self):
        """测试后清理"""
        print("\n=== 清理测试资源 ===")
        self.agent.cleanup()
        print("=== 测试完成 ===\n")

if __name__ == '__main__':
    unittest.main(verbosity=2) 