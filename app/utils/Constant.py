"""
此文件用于存储常量
"""
import datetime
import os
from enum import Enum

# 注意！！！ 枚举类常量使用先import,然后直接用[类名.变量名.value]的格式使用该变量
# 时区枚举类
class TimeZoneOptions(Enum):
    SHANGHAI = datetime.timezone(datetime.timedelta(hours=8), name="Asia/Shanghai")


# LLM翻译模型枚举类
class ModelOptions(Enum):
    DEEP_SEEK = "deepseek-ai/DeepSeek-R1"
    HUNYUAN = "tencent/Hunyuan-MT-7B"


# 大模型输出类型枚举类
class LLMOutputType(Enum):
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    ANALYSIS = "analysis"
    COMPARISON = "comparison"


# 领域关键词枚举类
class ArticleFiled(Enum):
    Cat_keys = " (cat:cs.IR OR cat:cs.CV OR cat:cs.LG OR cat:cs.CL OR cat:stat.ML OR cat:cs.CR OR cat:cs.AI)"
    RS_keys = " (ti:Recommend OR ti:RS OR ti:recommendation) "
    MM_keys = " ((ti:multi AND ti:modal) OR (ti:vision AND ti:language) OR ti:vlp OR ti:clip OR ti:blip OR ti:cross-modal) "
    LLM_keys = "(ti:LLMs OR ti:llms OR ti:llm OR (ti:large AND ti:language) OR ti:RAG OR (ti:retrieval AND ti:augmented) OR ti:bert OR ti:gpt OR ti:llama OR ti:tokenizer OR ti:tokenization OR ti:prompt OR ti:instruction OR abs:llm OR (abs:large AND abs:language))"
    Adversarial_keys = " (ti:attack OR ti:adversarial  OR ti:poison OR ti:backdoor OR ti:robust OR ti:safe OR ti:defense OR ti:security OR ti:vulnerability OR ti:jailbreak OR ti:hallucination) "


# 查询条件枚举类
class ArticleQuery(Enum):
    all_adversarial_query = ArticleFiled.Adversarial_keys.value + " AND " + ArticleFiled.Cat_keys.value
    RS_adversarial_query = ArticleFiled.RS_keys.value + " AND " + ArticleFiled.Adversarial_keys.value + " AND " + ArticleFiled.Cat_keys.value
    MM_adversarial_query = ArticleFiled.MM_keys.value + " AND " + ArticleFiled.Adversarial_keys.value + " AND " + ArticleFiled.Cat_keys.value
    LLM_adversarial_query = ArticleFiled.LLM_keys.value + " AND " + ArticleFiled.Adversarial_keys.value + " AND " + ArticleFiled.Cat_keys.value
    RS_query = ArticleFiled.RS_keys.value + " AND " + ArticleFiled.Cat_keys.value
    MM_query = ArticleFiled.MM_keys.value + " AND " + ArticleFiled.Cat_keys.value
    LLM_query = ArticleFiled.LLM_keys.value + " AND " + ArticleFiled.Cat_keys.value


# API密钥
API_KEY = os.environ.get('SILICONFLOW_API_KEY', 'sk-jrgzgilvqtrmchfdkpjmvktgejnvzonlrlilxcbammhamvav')
