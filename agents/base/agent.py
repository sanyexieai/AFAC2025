from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging
from .state import AgentState
from .protocol import A2AProtocol
from .message import Message, MessageType

class BaseAgent(ABC):
    """Agent基类，提供所有Agent共有的基础功能"""
    
    def __init__(self, name: str, config: Optional[Dict] = None):
        """
        初始化Agent
        
        Args:
            name: Agent名称
            config: Agent配置参数
        """
        self.name = name
        self.config = config or {}
        self.state = AgentState.IDLE
        self._setup_logger()
        self._protocol = A2AProtocol()
        self._setup_protocol_handlers()
        
    def _setup_logger(self) -> None:
        """设置日志记录器"""
        self.logger = logging.getLogger(self.name)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def _setup_protocol_handlers(self) -> None:
        """设置协议处理器"""
        # 注册消息处理器
        self._protocol.register_message_handler(
            MessageType.TASK,
            self._handle_task_message
        )
        self._protocol.register_message_handler(
            MessageType.RESULT,
            self._handle_result_message
        )
        self._protocol.register_message_handler(
            MessageType.ERROR,
            self._handle_error_message
        )
        self._protocol.register_message_handler(
            MessageType.STATUS,
            self._handle_status_message
        )
        self._protocol.register_message_handler(
            MessageType.REQUEST,
            self._handle_request_message
        )
        self._protocol.register_message_handler(
            MessageType.RESPONSE,
            self._handle_response_message
        )
        
        # 注册状态处理器
        self._protocol.register_state_handler(
            AgentState.IDLE,
            self._handle_idle_state
        )
        self._protocol.register_state_handler(
            AgentState.RUNNING,
            self._handle_running_state
        )
        self._protocol.register_state_handler(
            AgentState.ERROR,
            self._handle_error_state
        )
        self._protocol.register_state_handler(
            AgentState.COMPLETED,
            self._handle_completed_state
        )
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """
        执行Agent的主要任务
        
        Returns:
            任务执行结果
        """
        pass
    
    def validate(self, data: Any) -> bool:
        """
        验证输入数据或输出结果
        
        Args:
            data: 待验证的数据
            
        Returns:
            验证是否通过
        """
        try:
            return self._validate_impl(data)
        except Exception as e:
            self.log_error(f"Validation error: {str(e)}")
            return False
    
    @abstractmethod
    def _validate_impl(self, data: Any) -> bool:
        """
        具体的验证实现
        
        Args:
            data: 待验证的数据
            
        Raises:
            ValueError: 验证失败时抛出
        """
        pass
    
    def update_state(self, new_state: AgentState) -> None:
        """
        更新Agent状态
        
        Args:
            new_state: 新状态
        """
        old_state = self.state
        self.state = new_state
        self._protocol.handle_state_change(old_state, new_state)
        self.logger.info(f"State changed from {old_state.value} to {new_state.value}")
    
    def log_error(self, error: str) -> None:
        """
        记录错误日志
        
        Args:
            error: 错误信息
        """
        self.logger.error(error)
        self.update_state(AgentState.ERROR)
    
    def send_message(self, receiver: str, message_type: MessageType, content: Any) -> None:
        """发送消息给其他Agent"""
        message = Message(
            type=message_type,
            sender=self.name,
            receiver=receiver,
            content=content
        )
        self._protocol.send_message(message)
    
    def receive_message(self) -> Optional[Message]:
        """接收消息"""
        return self._protocol.receive_message(self.name)
    
    def _handle_task_message(self, message: Message) -> None:
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
    
    def _handle_result_message(self, message: Message) -> None:
        """处理结果消息"""
        self.logger.info(f"Received result from {message.sender}: {message.content}")
    
    def _handle_error_message(self, message: Message) -> None:
        """处理错误消息"""
        self.logger.error(f"Received error from {message.sender}: {message.content}")
    
    def _handle_status_message(self, message: Message) -> None:
        """处理状态消息"""
        self.logger.info(f"Received status from {message.sender}: {message.content}")
    
    def _handle_request_message(self, message: Message) -> None:
        """处理请求消息"""
        self.logger.info(f"Received request from {message.sender}: {message.content}")
    
    def _handle_response_message(self, message: Message) -> None:
        """处理响应消息"""
        self.logger.info(f"Received response from {message.sender}: {message.content}")
    
    def _handle_idle_state(self, old_state: AgentState, new_state: AgentState) -> None:
        """处理空闲状态"""
        self.logger.info("Agent is now idle")
    
    def _handle_running_state(self, old_state: AgentState, new_state: AgentState) -> None:
        """处理运行状态"""
        self.logger.info("Agent is now running")
    
    def _handle_error_state(self, old_state: AgentState, new_state: AgentState) -> None:
        """处理错误状态"""
        self.logger.error("Agent encountered an error")
    
    def _handle_completed_state(self, old_state: AgentState, new_state: AgentState) -> None:
        """处理完成状态"""
        self.logger.info("Agent has completed its task")
    
    def cleanup(self) -> None:
        """清理Agent资源"""
        self.logger.info("Cleaning up resources")
        self.update_state(AgentState.IDLE) 