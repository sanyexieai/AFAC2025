from enum import Enum

class AgentState(Enum):
    """Agent状态枚举"""
    IDLE = "idle"           # 空闲状态
    RUNNING = "running"     # 运行状态
    ERROR = "error"         # 错误状态
    COMPLETED = "completed" # 完成状态 