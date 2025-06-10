# AFAC2025 - 智能金融研报生成系统

## 项目概述
本项目实现了一个基于多Agent系统的智能金融研报生成系统，能够自动生成三类研究报告：
- 公司/个股研究报告
- 行业/子行业研究报告
- 宏观经济/策略研究报告

## 系统架构
```
AFAC2025/
├── agents/                 # Agent系统核心组件
│   ├── base/              # 基础Agent组件
│   │   ├── agent.py      # BaseAgent基类
│   │   └── state.py      # Agent状态定义
│   ├── research/         # 数据收集Agent
│   │   ├── agent.py      # ResearchAgent实现
│   │   ├── collectors/   # 数据采集器
│   │   └── validators/   # 数据验证器
│   ├── analysis/         # 数据分析Agent
│   │   ├── agent.py      # AnalysisAgent实现
│   │   ├── analyzers/    # 分析器
│   │   └── validators/   # 分析结果验证器
│   ├── writing/          # 报告生成Agent
│   │   ├── agent.py      # WritingAgent实现
│   │   ├── generators/   # 生成器
│   │   └── templates/    # 报告模板
│   ├── review/           # 质量审查Agent
│   │   ├── agent.py      # ReviewAgent实现
│   │   ├── checkers/     # 检查器
│   │   └── validators/   # 审查结果验证器
│   └── orchestrator/     # Agent协调器
│       ├── agent.py      # Orchestrator实现
│       ├── scheduler.py  # 任务调度器
│       └── monitor.py    # 状态监控器
├── data/                  # 数据处理模块
│   ├── collectors/       # 数据采集器
│   ├── processors/       # 数据处理器
│   └── storage/         # 数据存储
├── models/               # 模型组件
│   ├── llm/             # 语言模型集成
│   └── tools/           # 工具集成
├── reports/             # 报告生成
│   ├── templates/       # 报告模板
│   ├── generators/      # 报告生成器
│   └── visualizations/  # 图表生成
├── utils/               # 工具函数
├── config/             # 配置文件
└── tests/              # 测试用例
```

## 核心功能

### 1. 多Agent协同系统
- 基于A2A协议的Agent间通信
- 任务分解和分配机制
- 反馈循环机制

### 2. 数据处理系统
- 多源数据采集（Wind、国家统计局、交易所等）
- 数据清洗和标准化
- 结构化存储和缓存

### 3. 模型系统
- 开源大模型集成
- RAG（检索增强生成）实现
- 金融分析工具集成

### 4. 报告生成系统
- 多模态输出（文本+图表）
- 专业格式支持
- 引用和溯源机制

## 工作流程
```
[数据收集] -> [数据分析] -> [报告生成] -> [质量审查] -> [报告优化]
    ↑            ↑            ↑            ↑            ↑
    └────────────┴────────────┴────────────┴────────────┘
                    [反馈循环]
```

## 技术特点

### 1. 多Agent协同
- 使用MCP协议优化模型上下文
- 实现A2A协议提升Agent协作
- 集成RAG技术增强生成质量

### 2. 数据集成
- 多源数据采集和验证
- 实时数据更新和同步
- 数据质量保证机制

### 3. 报告生成
- 多模态内容生成
- 专业格式规范
- 自动图表生成

### 4. 质量控制
- 自动质量检查
- 人工审核接口
- 持续改进机制

## 安装和使用

### 环境要求
- Python 3.8+
- 相关依赖见 requirements.txt

### 安装步骤
1. 克隆仓库
```bash
git clone https://github.com/sanyexieai/AFAC2025.git
cd AFAC2025
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件配置相关参数
```

### 使用方法
1. 生成公司研报
```bash
python main.py --type company --target "00020.HK" --timeframe "2023Q1"
```

2. 生成行业研报
```bash
python main.py --type industry --target "互联网" --timeframe "2023H1"
```

3. 生成宏观研报
```bash
python main.py --type macro --target "经济政策" --timeframe "2023Y"
```

## 开发指南
- 遵循PEP 8编码规范
- 使用类型注解
- 编写单元测试

## 贡献指南
- Fork 项目
- 创建特性分支
- 提交更改
- 发起 Pull Request

## 许可证
MIT License 