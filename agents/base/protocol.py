from typing import Any, Callable, Dict, Optional
from .message import Message, MessageType, MessageQueue
from .state import AgentState

class A2AProtocol:
    """Agent2Agent 协议实现"""
    
    def __init__(self):
        self._message_queue = MessageQueue()
        self._message_handlers: Dict[MessageType, Callable] = {}
        self._state_handlers: Dict[AgentState, Callable] = {}
    
    def register_message_handler(self, message_type: MessageType, handler: Callable) -> None:
        """注册消息处理器"""
        self._message_handlers[message_type] = handler
    
    def register_state_handler(self, state: AgentState, handler: Callable) -> None:
        """注册状态处理器"""
        self._state_handlers[state] = handler
    
    def send_message(self, message: Message) -> None:
        """发送消息"""
        self._message_queue.send(message)
    
    def receive_message(self, agent_id: str) -> Optional[Message]:
        """接收消息"""
        return self._message_queue.receive(agent_id)
    
    def handle_message(self, message: Message) -> None:
        """处理消息"""
        handler = self._message_handlers.get(message.type)
        if handler:
            handler(message)
    
    def handle_state_change(self, old_state: AgentState, new_state: AgentState) -> None:
        """处理状态变化"""
        handler = self._state_handlers.get(new_state)
        if handler:
            handler(old_state, new_state)
    
    def create_task_message(self, sender: str, receiver: str, task: Any) -> Message:
        """创建任务消息"""
        return Message(
            type=MessageType.TASK,
            sender=sender,
            receiver=receiver,
            content=task
        )
    
    def create_result_message(self, sender: str, receiver: str, result: Any) -> Message:
        """创建结果消息"""
        return Message(
            type=MessageType.RESULT,
            sender=sender,
            receiver=receiver,
            content=result
        )
    
    def create_error_message(self, sender: str, receiver: str, error: Exception) -> Message:
        """创建错误消息"""
        return Message(
            type=MessageType.ERROR,
            sender=sender,
            receiver=receiver,
            content=str(error)
        )
    
    def create_status_message(self, sender: str, receiver: str, status: AgentState) -> Message:
        """创建状态消息"""
        return Message(
            type=MessageType.STATUS,
            sender=sender,
            receiver=receiver,
            content=status.value
        )
    
    def create_request_message(self, sender: str, receiver: str, request: Any) -> Message:
        """创建请求消息"""
        return Message(
            type=MessageType.REQUEST,
            sender=sender,
            receiver=receiver,
            content=request
        )
    
    def create_response_message(self, sender: str, receiver: str, response: Any) -> Message:
        """创建响应消息"""
        return Message(
            type=MessageType.RESPONSE,
            sender=sender,
            receiver=receiver,
            content=response
        ) 