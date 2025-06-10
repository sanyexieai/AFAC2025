# Agent2Agent (A2A) 协议

## 概述

A2A 协议是一个用于 Agent 之间通信的轻量级协议，它提供了一套标准化的消息传递机制，使不同的 Agent 能够进行可靠的信息交换和任务协作。该协议支持异步通信、状态管理和错误处理，适用于复杂的多 Agent 系统。

## 核心组件

### 1. 消息类型 (MessageType)

```python
class MessageType(Enum):
    TASK = "task"           # 任务消息
    RESULT = "result"       # 结果消息
    ERROR = "error"         # 错误消息
    STATUS = "status"       # 状态消息
    REQUEST = "request"     # 请求消息
    RESPONSE = "response"   # 响应消息
```

### 2. 消息格式 (Message)

```python
@dataclass
class Message:
    id: str                 # 消息唯一标识
    type: MessageType       # 消息类型
    sender: str            # 发送者ID
    receiver: str          # 接收者ID
    content: Any           # 消息内容
    timestamp: datetime    # 时间戳
    metadata: Dict         # 元数据
```

### 3. 消息队列 (MessageQueue)

消息队列负责管理消息的发送和接收，提供以下主要功能：
- 消息发送 (send)
- 消息接收 (receive)
- 消息预览 (peek)
- 队列清理 (clear)

### 4. 协议实现 (A2AProtocol)

A2AProtocol 类提供了完整的协议实现，包括：
- 消息处理器注册
- 状态处理器注册
- 消息发送和接收
- 消息处理
- 状态变化处理

## 使用方法

### 1. 基本使用

```python
from agents.base import BaseAgent, MessageType

class MyAgent(BaseAgent):
    def __init__(self, name: str):
        super().__init__(name)
    
    def execute(self, task: Any) -> Any:
        # 发送任务消息
        self.send_message(
            receiver="target_agent",
            message_type=MessageType.TASK,
            content=task
        )
        
        # 接收响应
        response = self.receive_message()
        if response:
            return response.content
```

### 2. 消息处理

```python
class MyAgent(BaseAgent):
    def _handle_task_message(self, message: Message) -> None:
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
```

### 3. 状态管理

```python
class MyAgent(BaseAgent):
    def execute(self, task: Any) -> Any:
        self.update_state(AgentState.RUNNING)
        try:
            result = self._process_task(task)
            self.update_state(AgentState.COMPLETED)
            return result
        except Exception as e:
            self.update_state(AgentState.ERROR)
            raise
```

## 最佳实践

1. **错误处理**
   - 始终使用 try-except 块处理可能的异常
   - 发送错误消息而不是静默失败
   - 更新 Agent 状态以反映错误情况

2. **消息验证**
   - 在发送消息前验证消息内容
   - 在接收消息时验证消息格式
   - 使用元数据传递额外的验证信息

3. **状态管理**
   - 及时更新 Agent 状态
   - 处理所有可能的状态转换
   - 记录状态变化日志

4. **资源清理**
   - 在任务完成后清理资源
   - 在错误发生时进行适当的清理
   - 使用 cleanup 方法确保资源释放

## 示例场景

### 1. 任务分配

```python
# 发送任务
orchestrator.send_message(
    receiver="research_agent",
    message_type=MessageType.TASK,
    content={
        "type": "market_data",
        "target": "AAPL",
        "timeframe": "1d"
    }
)

# 接收结果
response = orchestrator.receive_message()
if response and response.type == MessageType.RESULT:
    market_data = response.content
```

### 2. 状态同步

```python
# 发送状态更新
agent.send_message(
    receiver="monitor",
    message_type=MessageType.STATUS,
    content=AgentState.RUNNING.value
)

# 处理状态变化
def _handle_status_message(self, message: Message) -> None:
    new_state = AgentState(message.content)
    self.logger.info(f"Agent {message.sender} state changed to {new_state.value}")
```

### 3. 错误处理

```python
try:
    result = agent.execute(task)
except Exception as e:
    agent.send_message(
        receiver="error_handler",
        message_type=MessageType.ERROR,
        content={
            "error": str(e),
            "task": task,
            "timestamp": datetime.now().isoformat()
        }
    )
```

## 注意事项

1. **消息队列管理**
   - 定期清理过期的消息
   - 监控队列大小
   - 处理队列满的情况

2. **性能考虑**
   - 避免发送过大的消息
   - 使用异步处理大量消息
   - 实现消息优先级机制

3. **安全性**
   - 验证消息发送者
   - 加密敏感信息
   - 实现访问控制

4. **可扩展性**
   - 支持自定义消息类型
   - 允许扩展消息格式
   - 提供插件机制 