import unittest
from typing import Any, Dict, List
from agents.research.agent import ResearchAgent
from agents.base import BaseAgent, MessageType, AgentState
from agents.base.message import Message

class MockAnalysisAgent(BaseAgent):
    """模拟分析代理，用于测试与研究代理的交互"""
    
    def __init__(self, name: str = "analysis_agent"):
        super().__init__(name)
        self.received_messages: List[Message] = []
    
    def _validate_impl(self) -> bool:
        """验证实现"""
        return True
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务"""
        return {"status": "success", "result": "mock result"}
    
    def handle_message(self, message: Message) -> None:
        """记录接收到的消息"""
        self.received_messages.append(message)
    
    def send_message(self, target: str, msg_type: MessageType, content: Any) -> None:
        """发送消息到目标代理"""
        message = Message(
            sender=self.name,
            content=content,
            type=msg_type
        )
        self.received_messages.append(message)

class TestResearchAgentIntegration(unittest.TestCase):
    """ResearchAgent集成测试"""
    
    def setUp(self):
        """测试前准备"""
        print("\n=== 开始集成测试 ResearchAgent ===")
        self.research_agent = ResearchAgent()
        self.analysis_agent = MockAnalysisAgent()
        print("初始化完成：研究代理和分析代理")
    
    def test_market_data_analysis_flow(self):
        """测试市场数据分析流程"""
        print("\n测试市场数据分析流程...")
        # 分析代理请求市场数据
        request = Message(
            sender=self.analysis_agent.name,
            content={
                "action": "get_data",
                "task": {
                    "type": "market",
                    "target": "000001",
                    "timeframe": "1d",
                    "fields": ["open", "close", "high", "low", "volume"]
                }
            },
            type=MessageType.REQUEST
        )
        
        print(f"分析代理发送请求: {request.content}")
        # 研究代理处理请求
        self.research_agent.handle_message(request)
        
        # 验证研究代理的状态
        self.assertEqual(self.research_agent.state, AgentState.COMPLETED)
        print(f"研究代理状态: {self.research_agent.state.value}")
        
        # 验证分析代理是否收到响应
        self.assertEqual(len(self.analysis_agent.received_messages), 1)
        response = self.analysis_agent.received_messages[0]
        self.assertEqual(response.type, MessageType.RESULT)
        self.assertIn("data", response.content)
        print(f"分析代理收到响应: {response.content}")
        print("市场数据分析流程测试通过！")
    
    def test_financial_data_analysis_flow(self):
        """测试财务数据分析流程"""
        print("\n测试财务数据分析流程...")
        # 分析代理请求财务数据
        request = Message(
            sender=self.analysis_agent.name,
            content={
                "action": "get_data",
                "task": {
                    "type": "financial",
                    "target": "000001",
                    "timeframe": "2023Q1",
                    "fields": ["revenue", "profit", "assets", "liabilities", "equity"]
                }
            },
            type=MessageType.REQUEST
        )
        
        print(f"分析代理发送请求: {request.content}")
        # 研究代理处理请求
        self.research_agent.handle_message(request)
        
        # 验证研究代理的状态
        self.assertEqual(self.research_agent.state, AgentState.COMPLETED)
        print(f"研究代理状态: {self.research_agent.state.value}")
        
        # 验证分析代理是否收到响应
        self.assertEqual(len(self.analysis_agent.received_messages), 1)
        response = self.analysis_agent.received_messages[0]
        self.assertEqual(response.type, MessageType.RESULT)
        self.assertIn("data", response.content)
        print(f"分析代理收到响应: {response.content}")
        print("财务数据分析流程测试通过！")
    
    def test_news_data_analysis_flow(self):
        """测试新闻数据分析流程"""
        print("\n测试新闻数据分析流程...")
        # 分析代理请求新闻数据
        request = Message(
            sender=self.analysis_agent.name,
            content={
                "action": "get_data",
                "task": {
                    "type": "news",
                    "target": "000001",
                    "timeframe": "1d",
                    "fields": ["title", "content", "source", "url", "publish_time", "sentiment"]
                }
            },
            type=MessageType.REQUEST
        )
        
        print(f"分析代理发送请求: {request.content}")
        # 研究代理处理请求
        self.research_agent.handle_message(request)
        
        # 验证研究代理的状态
        self.assertEqual(self.research_agent.state, AgentState.COMPLETED)
        print(f"研究代理状态: {self.research_agent.state.value}")
        
        # 验证分析代理是否收到响应
        self.assertEqual(len(self.analysis_agent.received_messages), 1)
        response = self.analysis_agent.received_messages[0]
        self.assertEqual(response.type, MessageType.RESULT)
        self.assertIn("news", response.content)
        print(f"分析代理收到响应: {response.content}")
        print("新闻数据分析流程测试通过！")
    
    def test_error_handling_flow(self):
        """测试错误处理流程"""
        # 分析代理发送无效请求
        request = Message(
            sender=self.analysis_agent.name,
            content={
                "action": "get_data",
                "task": {
                    "type": "invalid",
                    "target": "000001"
                }
            },
            type=MessageType.REQUEST
        )
        
        # 研究代理处理请求
        self.research_agent.handle_message(request)
        
        # 验证研究代理的状态
        self.assertEqual(self.research_agent.state, AgentState.ERROR)
        
        # 验证分析代理是否收到错误响应
        self.assertEqual(len(self.analysis_agent.received_messages), 1)
        response = self.analysis_agent.received_messages[0]
        self.assertEqual(response.type, MessageType.ERROR)
    
    def test_cleanup_flow(self):
        """测试清理流程"""
        # 分析代理发送清理命令
        request = Message(
            sender=self.analysis_agent.name,
            content={
                "action": "cleanup"
            },
            type=MessageType.COMMAND
        )
        
        # 研究代理处理请求
        self.research_agent.handle_message(request)
        
        # 验证研究代理的状态
        self.assertEqual(self.research_agent.state, AgentState.IDLE)
        
        # 验证分析代理是否收到成功响应
        self.assertEqual(len(self.analysis_agent.received_messages), 1)
        response = self.analysis_agent.received_messages[0]
        self.assertEqual(response.type, MessageType.RESULT)
        self.assertEqual(response.content["status"], "success")
    
    def test_concurrent_requests(self):
        """测试并发请求处理"""
        print("\n测试并发请求处理...")
        # 分析代理发送多个并发请求
        requests = [
            Message(
                sender=self.analysis_agent.name,
                content={
                    "action": "get_data",
                    "task": {
                        "type": "market",
                        "target": "000001",
                        "timeframe": "1d"
                    }
                },
                type=MessageType.REQUEST
            ),
            Message(
                sender=self.analysis_agent.name,
                content={
                    "action": "get_data",
                    "task": {
                        "type": "financial",
                        "target": "000001",
                        "timeframe": "2023Q1"
                    }
                },
                type=MessageType.REQUEST
            ),
            Message(
                sender=self.analysis_agent.name,
                content={
                    "action": "get_data",
                    "task": {
                        "type": "news",
                        "target": "000001",
                        "timeframe": "1d"
                    }
                },
                type=MessageType.REQUEST
            )
        ]
        
        print("发送并发请求...")
        # 研究代理处理所有请求
        for request in requests:
            print(f"处理请求: {request.content}")
            self.research_agent.handle_message(request)
        
        # 验证研究代理的状态
        self.assertEqual(self.research_agent.state, AgentState.COMPLETED)
        print(f"研究代理状态: {self.research_agent.state.value}")
        
        # 验证分析代理是否收到所有响应
        self.assertEqual(len(self.analysis_agent.received_messages), 3)
        for i, response in enumerate(self.analysis_agent.received_messages):
            self.assertEqual(response.type, MessageType.RESULT)
            print(f"响应 {i+1}: {response.content}")
        print("并发请求处理测试通过！")
    
    def tearDown(self):
        """测试后清理"""
        print("\n=== 清理测试资源 ===")
        self.research_agent.cleanup()
        self.analysis_agent.cleanup()
        print("=== 集成测试完成 ===\n")

if __name__ == '__main__':
    unittest.main(verbosity=2) 