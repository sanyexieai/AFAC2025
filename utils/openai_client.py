import json
import logging
from typing import Dict, Any, List
import openai
from config.config import (
    OPENAI_API_KEY,
    OPENAI_API_BASE,
    OPENAI_API_MODEL,
    SYSTEM_PROMPTS,
    ANALYSIS_PROMPTS,
    WRITING_PROMPTS,
    REVIEW_PROMPTS
)

class OpenAIClient:
    """OpenAI API 客户端"""
    
    def __init__(self, model_type: str = "openai"):
        """初始化客户端
        
        Args:
            model_type: 模型类型，可选 "openai" 或 "deepseek"
        """
        self.model_type = model_type
        self.client = openai.OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_API_BASE
        )
        self.model = OPENAI_API_MODEL
        self.logger = logging.getLogger(__name__)
    
    def analyze(self, data_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用 GPT 分析数据
        
        Args:
            data_type: 数据类型 (market/financial/news)
            data: 要分析的数据
            
        Returns:
            分析结果
        """
        try:
            prompt = ANALYSIS_PROMPTS[data_type].format(data=json.dumps(data, ensure_ascii=False, indent=2))
            response = self._call_gpt(prompt, SYSTEM_PROMPTS["analysis"])
            return self._parse_result(response)
        except Exception as e:
            self.logger.error(f"分析数据失败: {str(e)}")
            raise
    
    def write_report(self, report_type: str, target: str, analysis_results: Dict[str, Any]) -> str:
        """
        使用 GPT 生成研报
        
        Args:
            report_type: 研报类型 (company/industry/macro)
            target: 目标对象
            analysis_results: 分析结果
            
        Returns:
            研报内容
        """
        try:
            prompt = WRITING_PROMPTS[report_type].format(
                target=target,
                **analysis_results
            )
            response = self._call_gpt(prompt, SYSTEM_PROMPTS["writing"])
            return response
        except Exception as e:
            self.logger.error(f"生成报告失败: {str(e)}")
            raise
    
    def review_report(self, report_type: str, target: str, content: str, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用 GPT 审核研报
        
        Args:
            report_type: 研报类型 (company/industry/macro)
            target: 目标对象
            content: 研报内容
            analysis_results: 分析结果
            
        Returns:
            审核结果
        """
        try:
            prompt = REVIEW_PROMPTS[report_type].format(
                target=target,
                content=content,
                **analysis_results
            )
            response = self._call_gpt(prompt, SYSTEM_PROMPTS["review"])
            return self._parse_result(response)
        except Exception as e:
            self.logger.error(f"审核报告失败: {str(e)}")
            raise
    
    def _call_gpt(self, prompt: str, system_prompt: str) -> str:
        """调用GPT API (openai>=1.0.0 新接口)"""
        try:
            if self.model_type == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                return response.choices[0].message.content
            elif self.model_type == "deepseek":
                # 假设 deepseek 的 API 调用方式与 openai 类似，但模型名称不同
                response = self.client.chat.completions.create(
                    model="deepseek-chat",  # 替换为实际的 deepseek 模型名称
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                return response.choices[0].message.content
            else:
                raise ValueError(f"不支持的模型类型: {self.model_type}")
        except Exception as e:
            self.logger.error(f"GPT API 调用失败: {str(e)}")
            raise
    
    def _parse_result(self, response: str) -> Dict[str, Any]:
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"content": response} 