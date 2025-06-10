import unittest
from typing import Dict, List
from agents.research.collectors.financial import FinancialDataCollector

class TestFinancialDataCollector(unittest.TestCase):
    """财务数据采集器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.collector = FinancialDataCollector()
    
    def test_collect_basic(self):
        """测试基本数据收集"""
        data = self.collector.collect(
            target="000001",
            timeframe="2023Q1",
            fields=["revenue", "profit", "assets", "liabilities", "equity"]
        )
        
        # 验证返回数据结构
        self.assertIsInstance(data, dict)
        self.assertEqual(data["company"], "000001")
        self.assertEqual(data["period"], "2023Q1")
        self.assertIn("data", data)
        
        # 验证数据字段
        financial_data = data["data"]
        self.assertIn("revenue", financial_data)
        self.assertIn("profit", financial_data)
        self.assertIn("assets", financial_data)
        self.assertIn("liabilities", financial_data)
        self.assertIn("equity", financial_data)
        
        # 验证数据类型
        self.assertIsInstance(financial_data["revenue"], (int, float))
        self.assertIsInstance(financial_data["profit"], (int, float))
        self.assertIsInstance(financial_data["assets"], (int, float))
        self.assertIsInstance(financial_data["liabilities"], (int, float))
        self.assertIsInstance(financial_data["equity"], (int, float))
        
        # 验证数据合理性
        self.assertEqual(
            financial_data["assets"],
            financial_data["liabilities"] + financial_data["equity"]
        )
    
    def test_collect_partial_fields(self):
        """测试部分字段收集"""
        data = self.collector.collect(
            target="000001",
            timeframe="2023Q1",
            fields=["revenue", "profit"]
        )
        
        # 验证返回数据结构
        self.assertIsInstance(data, dict)
        self.assertEqual(data["company"], "000001")
        self.assertEqual(data["period"], "2023Q1")
        self.assertIn("data", data)
        
        # 验证数据字段
        financial_data = data["data"]
        self.assertIn("revenue", financial_data)
        self.assertIn("profit", financial_data)
        self.assertNotIn("assets", financial_data)
        self.assertNotIn("liabilities", financial_data)
        self.assertNotIn("equity", financial_data)
    
    def test_validate_data(self):
        """测试数据验证"""
        # 有效数据
        valid_data = {
            "company": "000001",
            "period": "2023Q1",
            "data": {
                "revenue": 1000000000.0,
                "profit": 100000000.0,
                "assets": 5000000000.0,
                "liabilities": 2000000000.0,
                "equity": 3000000000.0
            }
        }
        self.assertTrue(self.collector.validate(valid_data))
        
        # 无效数据 - 缺少必要字段
        invalid_data1 = {
            "company": "000001",
            "period": "2023Q1"
        }
        self.assertFalse(self.collector.validate(invalid_data1))
        
        # 无效数据 - 数据类型错误
        invalid_data2 = {
            "company": "000001",
            "period": "2023Q1",
            "data": {
                "revenue": "1000000000.0",
                "profit": 100000000.0,
                "assets": 5000000000.0,
                "liabilities": 2000000000.0,
                "equity": 3000000000.0
            }
        }
        self.assertFalse(self.collector.validate(invalid_data2))
        
        # 无效数据 - 数据不合理
        invalid_data3 = {
            "company": "000001",
            "period": "2023Q1",
            "data": {
                "revenue": 1000000000.0,
                "profit": 100000000.0,
                "assets": 5000000000.0,
                "liabilities": 2000000000.0,
                "equity": 2000000000.0  # 资产不等于负债加权益
            }
        }
        self.assertFalse(self.collector.validate(invalid_data3))

if __name__ == '__main__':
    unittest.main() 