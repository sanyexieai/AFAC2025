import unittest
from typing import Dict, List
from agents.research.collectors.market import MarketDataCollector

class TestMarketDataCollector(unittest.TestCase):
    """市场数据采集器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.collector = MarketDataCollector()
    
    def test_collect_basic(self):
        """测试基本数据收集"""
        data = self.collector.collect(
            target="000001",
            timeframe="1d",
            fields=["open", "close", "high", "low", "volume"]
        )
        
        # 验证返回数据结构
        self.assertIsInstance(data, dict)
        self.assertEqual(data["code"], "000001")
        self.assertEqual(data["timeframe"], "1d")
        self.assertIn("data", data)
        
        # 验证数据字段
        market_data = data["data"]
        self.assertIn("open", market_data)
        self.assertIn("close", market_data)
        self.assertIn("high", market_data)
        self.assertIn("low", market_data)
        self.assertIn("volume", market_data)
        
        # 验证数据类型
        self.assertIsInstance(market_data["open"], (int, float))
        self.assertIsInstance(market_data["close"], (int, float))
        self.assertIsInstance(market_data["high"], (int, float))
        self.assertIsInstance(market_data["low"], (int, float))
        self.assertIsInstance(market_data["volume"], (int, float))
        
        # 验证数据合理性
        self.assertGreaterEqual(market_data["high"], market_data["low"])
        self.assertGreaterEqual(market_data["high"], market_data["open"])
        self.assertGreaterEqual(market_data["high"], market_data["close"])
        self.assertLessEqual(market_data["low"], market_data["open"])
        self.assertLessEqual(market_data["low"], market_data["close"])
        self.assertGreaterEqual(market_data["volume"], 0)
    
    def test_collect_partial_fields(self):
        """测试部分字段收集"""
        data = self.collector.collect(
            target="000001",
            timeframe="1d",
            fields=["open", "close"]
        )
        
        # 验证返回数据结构
        self.assertIsInstance(data, dict)
        self.assertEqual(data["code"], "000001")
        self.assertEqual(data["timeframe"], "1d")
        self.assertIn("data", data)
        
        # 验证数据字段
        market_data = data["data"]
        self.assertIn("open", market_data)
        self.assertIn("close", market_data)
        self.assertNotIn("high", market_data)
        self.assertNotIn("low", market_data)
        self.assertNotIn("volume", market_data)
    
    def test_validate_data(self):
        """测试数据验证"""
        # 有效数据
        valid_data = {
            "code": "000001",
            "timeframe": "1d",
            "data": {
                "open": 100.0,
                "close": 101.0,
                "high": 102.0,
                "low": 99.0,
                "volume": 1000000
            }
        }
        self.assertTrue(self.collector.validate(valid_data))
        
        # 无效数据 - 缺少必要字段
        invalid_data1 = {
            "code": "000001",
            "timeframe": "1d"
        }
        self.assertFalse(self.collector.validate(invalid_data1))
        
        # 无效数据 - 数据类型错误
        invalid_data2 = {
            "code": "000001",
            "timeframe": "1d",
            "data": {
                "open": "100.0",
                "close": 101.0,
                "high": 102.0,
                "low": 99.0,
                "volume": 1000000
            }
        }
        self.assertFalse(self.collector.validate(invalid_data2))
        
        # 无效数据 - 数据不合理
        invalid_data3 = {
            "code": "000001",
            "timeframe": "1d",
            "data": {
                "open": 100.0,
                "close": 101.0,
                "high": 98.0,
                "low": 99.0,
                "volume": 1000000
            }
        }
        self.assertFalse(self.collector.validate(invalid_data3))

if __name__ == '__main__':
    unittest.main() 