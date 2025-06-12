from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
import logging
from langchain.tools import BaseTool
from langchain.agents import AgentExecutor, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.chat_models import ChatOpenAI

class LangChainCollector(ABC):
    """基于 LangChain 的数据采集器基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.tools: List[BaseTool] = []
        self._setup_tools()
        self._setup_agent()
    
    def _setup_tools(self) -> None:
        """设置工具集"""
        pass
    
    def _setup_agent(self) -> None:
        """设置 Agent"""
        # 获取系统提示词
        system_prompt = self._get_system_prompt()
        
        # 创建提示模板
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # 创建 ChatOpenAI 实例
        llm = ChatOpenAI(
            model_name=self.config.get("model_name", "gpt-3.5-turbo"),
            temperature=self.config.get("temperature", 0.7),
            api_key=self.config.get("api_key")
        )
        
        # 创建 Agent
        self.agent_executor = initialize_agent(
            tools=self.tools,
            llm=llm,
            agent="chat-conversational-react-description",
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3,
            early_stopping_method="generate",
            memory=None
        )
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        pass
    
    def collect(self, target: str, timeframe: str, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """收集数据
        
        Args:
            target: 目标（公司/行业）
            timeframe: 时间范围
            fields: 需要的字段列表
            
        Returns:
            Dict[str, Any]: 收集到的数据
        """
        try:
            # 构建输入
            inputs = {
                "input": f"收集关于 {target} 在 {timeframe} 期间的数据" + 
                        (f"，需要字段：{', '.join(fields)}" if fields else "")
            }
            
            # 执行 Agent
            result = self.agent_executor.invoke(inputs)
            
            # 验证结果
            self.validate(result)
            
            return result
        except Exception as e:
            raise Exception(f"Error collecting data: {str(e)}")
    
    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> bool:
        """验证数据
        
        Args:
            data: 要验证的数据
            
        Returns:
            bool: 验证是否通过
        """
        # 检查必要字段
        if not all(key in data for key in ["target", "timeframe"]):
            raise ValueError("Missing required fields")
        return True
    
    def cleanup(self) -> None:
        """清理资源"""
        self.logger.info("清理资源")
        for tool in self.tools:
            if hasattr(tool, "cleanup"):
                tool.cleanup() 