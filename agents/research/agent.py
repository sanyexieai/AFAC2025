import logging
from typing import Any, Dict, List, Optional
from ..base import BaseAgent, MessageType, AgentState
from .collectors.langchain.market import LangChainMarketCollector
from .collectors.langchain.financial import LangChainFinancialCollector
from .collectors.langchain.news import LangChainNewsCollector
from .validators.data_validator import DataValidator
from utils.openai_client import OpenAIClient

class ResearchAgent(BaseAgent):
    """研究代理，负责收集数据"""
    
    def __init__(self, name: str = "ResearchAgent", config: Dict[str, Any] = None):
        """初始化研究代理
        
        Args:
            name: 代理名称
            config: 配置信息
        """
        super().__init__(name, config)
        self.openai_client = OpenAIClient()
        self.logger = logging.getLogger(__name__)
        self._setup_collectors()
        self._setup_validators()
        self._setup_message_handlers()
    
    def _setup_collectors(self) -> None:
        """初始化数据采集器"""
        # 获取 LLM 配置
        llm_config = {
            "llm": self.openai_client.client,
            "max_results": self.config.get("max_results", 5)
        }
        
        # 初始化采集器
        self.collectors = {
            "market": LangChainMarketCollector({
                **llm_config,
                "api_key": self.config.get("market", {}).get("api_key", "")
            }),
            "financial": LangChainFinancialCollector({
                **llm_config,
                "api_key": self.config.get("financial", {}).get("api_key", "")
            }),
            "news": LangChainNewsCollector(llm_config)
        }
    
    def _setup_validators(self) -> None:
        """初始化数据验证器"""
        self.validator = DataValidator(self.config.get("validation", {}))
    
    def _setup_message_handlers(self) -> None:
        """初始化消息处理器"""
        self.message_handlers = {
            MessageType.TASK: self._handle_task_message,
            MessageType.REQUEST: self._handle_request_message,
            MessageType.COMMAND: self._handle_command_message,
            MessageType.ERROR: self._handle_error_message
        }
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行数据收集任务
        
        Args:
            task: 包含以下字段的字典：
                - type: 报告类型（company/industry/macro）
                - target: 目标（公司/行业/主题）
                - timeframe: 时间范围
                
        Returns:
            Dict[str, Any]: 收集到的数据
        """
        try:
            self.logger.info(f"开始收集{task['type']}数据...")
            
            # 验证任务
            self._validate_task(task)
            
            # 根据报告类型收集数据
            if task["type"] == "company":
                data = self._collect_company_data(task)
            elif task["type"] == "industry":
                data = self._collect_industry_data(task)
            else:  # macro
                data = self._collect_macro_data(task)
            
            self.logger.info(f"{task['type']}数据收集完成")
            return data
            
        except Exception as e:
            self.logger.error(f"数据收集失败: {str(e)}")
            raise
    
    def _validate_task(self, task: Dict[str, Any]):
        """验证任务格式"""
        required_fields = ["type", "target", "timeframe"]
        for field in required_fields:
            if field not in task:
                raise ValueError(f"缺少必要字段：{field}")
        
        if task["type"] not in ["company", "industry", "macro"]:
            raise ValueError(f"不支持的报告类型：{task['type']}")
    
    def _collect_company_data(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """收集公司数据
        
        Args:
            task: 任务信息
            
        Returns:
            Dict[str, Any]: 公司数据
        """
        # 收集市场数据
        market_data = self.market_collector.collect(
            target=task["target"],
            timeframe=task["timeframe"],
            fields=["open", "close", "high", "low", "volume"]
        )
        
        # 收集财务数据
        financial_data = self.financial_collector.collect(
            target=task["target"],
            timeframe=task["timeframe"],
            fields=["revenue", "profit", "assets", "liabilities", "equity"]
        )
        
        # 收集新闻数据
        news_data = self.news_collector.collect(
            target=task["target"],
            timeframe=task["timeframe"],
            fields=["title", "content", "source", "publish_time", "sentiment"]
        )
        
        return {
            "market_data": market_data,
            "financial_data": financial_data,
            "news_data": news_data
        }
    
    def _collect_industry_data(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """收集行业数据
        
        Args:
            task: 任务信息
            
        Returns:
            Dict[str, Any]: 行业数据
        """
        # 收集市场数据
        market_data = self.market_collector.collect(
            target=task["target"],
            timeframe=task["timeframe"],
            fields=["index", "change", "volume"]
        )
        
        # 收集新闻数据
        news_data = self.news_collector.collect(
            target=task["target"],
            timeframe=task["timeframe"],
            fields=["title", "content", "source", "publish_time", "sentiment"]
        )
        
        return {
            "market_data": market_data,
            "news_data": news_data
        }
    
    def _collect_macro_data(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """收集宏观数据
        
        Args:
            task: 任务信息
            
        Returns:
            Dict[str, Any]: 宏观数据
        """
        # 收集新闻数据
        news_data = self.news_collector.collect(
            target=task["target"],
            timeframe=task["timeframe"],
            fields=["title", "content", "source", "publish_time", "sentiment"]
        )
        
        return {
            "news_data": news_data
        }
    
    def _validate_impl(self, data: Dict[str, Any]) -> bool:
        """
        实现基类的抽象方法，验证数据格式
        
        Args:
            data: 要验证的数据
            
        Returns:
            验证是否通过
        """
        try:
            self._validate_task(data)
            return True
        except ValueError:
            return False
    
    def _handle_task_message(self, message: Any) -> None:
        """处理任务消息"""
        self.logger.info(f"Received task from {message.sender}: {message.content}")
        try:
            result = self.execute(message.content)
            self.send_message(
                message.sender,
                MessageType.RESULT,
                result
            )
        except Exception as e:
            self.send_message(
                message.sender,
                MessageType.ERROR,
                str(e)
            )
    
    def _handle_request_message(self, message: Any) -> None:
        """处理请求消息"""
        self.logger.info(f"Received request from {message.sender}: {message.content}")
        try:
            # 处理数据请求
            if message.content.get("action") == "get_data":
                result = self.execute(message.content["task"])
                self.send_message(
                    message.sender,
                    MessageType.RESULT,
                    result
                )
            # 处理状态请求
            elif message.content.get("action") == "get_status":
                self.send_message(
                    message.sender,
                    MessageType.RESULT,
                    {"state": self.state.value}
                )
            else:
                raise ValueError(f"Unsupported request action: {message.content.get('action')}")
        except Exception as e:
            self.send_message(
                message.sender,
                MessageType.ERROR,
                str(e)
            )
    
    def _handle_command_message(self, message: Any) -> None:
        """处理命令消息"""
        self.logger.info(f"Received command from {message.sender}: {message.content}")
        try:
            # 处理清理命令
            if message.content.get("action") == "cleanup":
                self.cleanup()
                self.send_message(
                    message.sender,
                    MessageType.RESULT,
                    {"status": "success"}
                )
            # 处理重置命令
            elif message.content.get("action") == "reset":
                self.update_state(AgentState.IDLE)
                self.send_message(
                    message.sender,
                    MessageType.RESULT,
                    {"status": "success"}
                )
            else:
                raise ValueError(f"Unsupported command action: {message.content.get('action')}")
        except Exception as e:
            self.send_message(
                message.sender,
                MessageType.ERROR,
                str(e)
            )
    
    def _handle_error_message(self, message: Any) -> None:
        """处理错误消息"""
        self.logger.error(f"Received error from {message.sender}: {message.content}")
        # 更新状态为错误
        self.update_state(AgentState.ERROR)
        # 记录错误信息
        self.log_error(f"Error from {message.sender}: {message.content}")
    
    def handle_message(self, message: Any) -> None:
        """
        处理接收到的消息
        
        Args:
            message: 接收到的消息
        """
        handler = self.message_handlers.get(message.type)
        if handler:
            handler(message)
        else:
            self.logger.warning(f"Unsupported message type: {message.type}")
    
    def cleanup(self) -> None:
        """清理资源"""
        self.logger.info("清理研究代理资源")
        self.state = AgentState.IDLE
        for collector in self.collectors.values():
            collector.cleanup()
        super().cleanup()
    
    @property
    def market_collector(self):
        return self.collectors["market"]
    
    @property
    def financial_collector(self):
        return self.collectors["financial"]
    
    @property
    def news_collector(self):
        return self.collectors["news"] 