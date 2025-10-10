"""
该文件用于调用大语言模型翻译
"""

import os

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.utils.Constant import LLMOutputType
from app.utils.Constant import ModelOptions

# ========== 常量 ==============
# 配置API密钥 - 请替换为您自己的API密钥
SILICONFLOW_API_KEY = os.environ.get('SILICONFLOW_API_KEY', 'sk-jrgzgilvqtrmchfdkpjmvktgejnvzonlrlilxcbammhamvav')
if SILICONFLOW_API_KEY == 'your-api-key-here':
    print("警告: 请设置您的SILICONFLOW_API_KEY环境变量或直接替换代码中的API密钥")

# 翻译模型选择
TRANSLATION_MODEL = ModelOptions.HUNYUAN.value


@retry(
    stop=stop_after_attempt(5),  # 增加重试次数
    wait=wait_exponential(multiplier=1, min=3, max=15),  # 增加等待时间
    retry=retry_if_exception_type(
        (requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout))
)
@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=3, max=15),
    retry=retry_if_exception_type(
        (requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout))
)
def call_llm_api(prompt, output_type=LLMOutputType.TRANSLATION, temperature=0.3):
    """
    调用大语言模型API
    
    Args:
        prompt (str): 提示词
        output_type (LLMOutputType): 输出类型
        temperature (float): 温度参数
        
    Returns:
        str: 模型输出结果
    """
    if not prompt or not SILICONFLOW_API_KEY:
        return ""

    url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {SILICONFLOW_API_KEY}",
        "Content-Type": "application/json"
    }

    # 根据输出类型设置不同的参数
    max_tokens_map = {
        LLMOutputType.TRANSLATION: 2000,
        LLMOutputType.SUMMARIZATION: 500,
        LLMOutputType.ANALYSIS: 1000,
        LLMOutputType.COMPARISON: 1500
    }

    max_tokens = max_tokens_map.get(output_type, 1000)

    payload = {
        "model": TRANSLATION_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    try:
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=10,
            max_retries=3
        )
        session.mount('https://', adapter)

        response = session.post(
            url,
            json=payload,
            headers=headers,
            timeout=(15, 90),
            verify=True,
            allow_redirects=True
        )
        response.raise_for_status()

        result = response.json()
        if result and "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"].strip()
        else:
            error_msg = f"LLM API返回空结果"
            if response:
                error_msg += f": {response.text[:500]}"
            print(error_msg)
            return ""

    except requests.exceptions.RequestException as e:
        print(f"LLM API调用失败: {str(e)}")
        if output_type != LLMOutputType.TRANSLATION:  # 翻译以外的功能失败时不重试，避免过度消耗API
            return ""
        raise

    except Exception as e:
        print(f"LLM API调用发生未知错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return ""
