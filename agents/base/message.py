from enum import Enum, auto
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid

class MessageType(Enum):
    """消息类型"""
    TASK = auto()      # 任务消息
    REQUEST = auto()   # 请求消息
    RESULT = auto()    # 结果消息
    ERROR = auto()     # 错误消息
    COMMAND = auto()   # 命令消息
    STATUS = auto()    # 状态消息
    RESPONSE = auto()  # 响应消息

@dataclass
class Message:
    """消息类"""
    sender: str
    content: Any
    type: MessageType
    receiver: str = field(default="")
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)

class MessageQueue:
    """消息队列"""
    
    def __init__(self):
        self.messages: List[Message] = []
    
    def push(self, message: Message) -> None:
        """添加消息到队列"""
        self.messages.append(message)
    
    def pop(self) -> Optional[Message]:
        """从队列中取出消息"""
        if not self.messages:
            return None
        return self.messages.pop(0)
    
    def peek(self) -> Optional[Message]:
        """查看队列中的第一条消息"""
        if not self.messages:
            return None
        return self.messages[0]
    
    def clear(self) -> None:
        """清空队列"""
        self.messages.clear()
    
    def is_empty(self) -> bool:
        """检查队列是否为空"""
        return len(self.messages) == 0
    
    def size(self) -> int:
        """获取队列大小"""
        return len(self.messages)

    def send(self, message: Message) -> None:
        """发送消息到接收者的队列"""
        self.push(message)
    
    def receive(self, agent_id: str) -> Optional[Message]:
        """从队列中接收消息"""
        for message in self.messages:
            if message.sender == agent_id:
                self.messages.remove(message)
                return message
        return None
    
    def peek_receive(self, agent_id: str) -> Optional[Message]:
        """查看队列中接收者的下一条消息但不移除"""
        for message in self.messages:
            if message.sender == agent_id:
                return message
        return None
    
    def clear_receive(self, agent_id: str) -> None:
        """清空指定Agent的消息队列"""
        self.messages = [message for message in self.messages if message.sender != agent_id] 