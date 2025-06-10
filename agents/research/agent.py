from typing import Any, Dict, List, Optional
from ..base import BaseAgent, MessageType, AgentState
from .collectors.market import MarketDataCollector
from .collectors.financial import FinancialDataCollector
from .collectors.news import NewsDataCollector
from .validators.data_validator import DataValidator

class ResearchAgent(BaseAgent):
    """数据收集Agent，负责从各种数据源获取所需信息"""
    
    def __init__(self, name: str = "research_agent", config: Optional[Dict] = None):
        super().__init__(name, config)
        self._setup_collectors()
        self._setup_validators()
        self._setup_message_handlers()
    
    def _setup_collectors(self) -> None:
        """初始化数据采集器"""
        self.collectors = {
            "market": MarketDataCollector(self.config.get("market", {})),
            "financial": FinancialDataCollector(self.config.get("financial", {})),
            "news": NewsDataCollector(self.config.get("news", {}))
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
    
    def execute(self, task: Dict) -> Dict:
        """
        执行数据收集任务
        
        Args:
            task: 任务信息，包含以下字段：
                - type: 数据类型 (market/financial/news)
                - target: 目标对象 (股票代码/公司名称等)
                - timeframe: 时间范围
                - fields: 需要收集的字段列表
        
        Returns:
            收集到的数据
        """
        self.update_state(AgentState.RUNNING)
        try:
            # 验证任务
            if not self._validate_impl(task):
                raise ValueError("Invalid task format")
            
            # 获取对应的采集器
            collector = self.collectors.get(task["type"])
            if not collector:
                raise ValueError(f"Unsupported data type: {task['type']}")
            
            # 收集数据
            data = collector.collect(
                target=task["target"],
                timeframe=task.get("timeframe"),
                fields=task.get("fields", [])
            )
            
            # 验证数据
            if not self.validator.validate(data):
                raise ValueError("Data validation failed")
            
            self.update_state(AgentState.COMPLETED)
            return data
            
        except Exception as e:
            self.log_error(f"Data collection failed: {str(e)}")
            raise
    
    def _validate_impl(self, data: Dict) -> bool:
        """
        验证任务格式
        
        Args:
            data: 待验证的任务数据
            
        Returns:
            验证是否通过
        """
        required_fields = ["type", "target"]
        return all(field in data for field in required_fields)
    
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