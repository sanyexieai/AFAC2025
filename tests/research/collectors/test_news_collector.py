import unittest
from typing import Dict, List
from datetime import datetime
from agents.research.collectors.news import NewsDataCollector

class TestNewsDataCollector(unittest.TestCase):
    """新闻数据采集器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.collector = NewsDataCollector()
    
    def test_collect_basic(self):
        """测试基本数据收集"""
        data = self.collector.collect(
            target="000001",
            timeframe="1d",
            fields=["title", "content", "source", "url", "publish_time", "sentiment"]
        )
        
        # 验证返回数据结构
        self.assertIsInstance(data, dict)
        self.assertEqual(data["target"], "000001")
        self.assertEqual(data["timeframe"], "1d")
        self.assertIn("news", data)
        
        # 验证新闻列表
        self.assertIsInstance(data["news"], list)
        self.assertGreater(len(data["news"]), 0)
        
        # 验证每条新闻的字段
        for news in data["news"]:
            self.assertIsInstance(news, dict)
            self.assertIn("title", news)
            self.assertIn("content", news)
            self.assertIn("source", news)
            self.assertIn("url", news)
            self.assertIn("publish_time", news)
            self.assertIn("sentiment", news)
            
            # 验证数据类型
            self.assertIsInstance(news["title"], str)
            self.assertIsInstance(news["content"], str)
            self.assertIsInstance(news["source"], str)
            self.assertIsInstance(news["url"], str)
            self.assertIsInstance(news["publish_time"], str)
            self.assertIsInstance(news["sentiment"], (int, float))
            
            # 验证数据合理性
            self.assertGreater(len(news["title"]), 0)
            self.assertGreater(len(news["content"]), 0)
            self.assertGreater(len(news["source"]), 0)
            self.assertGreater(len(news["url"]), 0)
            self.assertTrue(0 <= news["sentiment"] <= 1)
            
            # 验证时间格式
            try:
                datetime.fromisoformat(news["publish_time"])
            except ValueError:
                self.fail("Invalid datetime format")
    
    def test_collect_partial_fields(self):
        """测试部分字段收集"""
        data = self.collector.collect(
            target="000001",
            timeframe="1d",
            fields=["title", "sentiment"]
        )
        
        # 验证返回数据结构
        self.assertIsInstance(data, dict)
        self.assertEqual(data["target"], "000001")
        self.assertEqual(data["timeframe"], "1d")
        self.assertIn("news", data)
        
        # 验证新闻列表
        self.assertIsInstance(data["news"], list)
        self.assertGreater(len(data["news"]), 0)
        
        # 验证每条新闻的字段
        for news in data["news"]:
            self.assertIsInstance(news, dict)
            self.assertIn("title", news)
            self.assertIn("sentiment", news)
            self.assertNotIn("content", news)
            self.assertNotIn("source", news)
            self.assertNotIn("url", news)
            self.assertNotIn("publish_time", news)
    
    def test_validate_data(self):
        """测试数据验证"""
        # 有效数据
        valid_data = {
            "target": "000001",
            "timeframe": "1d",
            "news": [
                {
                    "title": "公司发布新产品",
                    "content": "公司今日发布新产品，预计将带来显著收入增长...",
                    "source": "新浪财经",
                    "url": "http://example.com/news/1",
                    "publish_time": datetime.now().isoformat(),
                    "sentiment": 0.8
                }
            ]
        }
        self.assertTrue(self.collector.validate(valid_data))
        
        # 无效数据 - 缺少必要字段
        invalid_data1 = {
            "target": "000001",
            "timeframe": "1d"
        }
        self.assertFalse(self.collector.validate(invalid_data1))
        
        # 无效数据 - 数据类型错误
        invalid_data2 = {
            "target": "000001",
            "timeframe": "1d",
            "news": [
                {
                    "title": 123,  # 应该是字符串
                    "content": "公司今日发布新产品，预计将带来显著收入增长...",
                    "source": "新浪财经",
                    "url": "http://example.com/news/1",
                    "publish_time": datetime.now().isoformat(),
                    "sentiment": 0.8
                }
            ]
        }
        self.assertFalse(self.collector.validate(invalid_data2))
        
        # 无效数据 - 情感值范围错误
        invalid_data3 = {
            "target": "000001",
            "timeframe": "1d",
            "news": [
                {
                    "title": "公司发布新产品",
                    "content": "公司今日发布新产品，预计将带来显著收入增长...",
                    "source": "新浪财经",
                    "url": "http://example.com/news/1",
                    "publish_time": datetime.now().isoformat(),
                    "sentiment": 1.5  # 超出范围
                }
            ]
        }
        self.assertFalse(self.collector.validate(invalid_data3))

if __name__ == '__main__':
    unittest.main() 