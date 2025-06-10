import unittest
from agents.research.agent import ResearchAgent
from agents.base import AgentState

class TestBasic(unittest.TestCase):
    """基本测试用例"""
    
    def setUp(self):
        """测试前准备"""
        self.agent = ResearchAgent()
    
    def test_agent_initialization(self):
        """测试Agent初始化"""
        self.assertIsNotNone(self.agent)
        self.assertEqual(self.agent.state, AgentState.IDLE)
    
    def test_agent_cleanup(self):
        """测试Agent清理"""
        self.agent.cleanup()
        self.assertEqual(self.agent.state, AgentState.IDLE)
    
    def tearDown(self):
        """测试后清理"""
        self.agent.cleanup()

if __name__ == '__main__':
    unittest.main() 