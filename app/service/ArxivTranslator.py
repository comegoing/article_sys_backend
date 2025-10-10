"""
该文件为文献检索后端接口的功能实现层
"""
import random
import re
import time

import arxiv
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.service.ExtractPaperLinks import extract_paper_links
from app.service.LLM import call_llm_api
from app.utils.Constant import *

# ============ 变量定义 ===================
# 翻译模型(此处为constant定义字典常量)
TRANSLATION_MODEL = ModelOptions.HUNYUAN.value


@retry(
    stop=stop_after_attempt(5),  # 增加重试次数
    wait=wait_exponential(multiplier=1, min=3, max=15),  # 增加等待时间
    retry=retry_if_exception_type(
        (requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout))
)


# 文献查询service层(功能层)
def arxivTranslate(start_date, end_date, choice, max_results):
    # 默认值
    query = ArticleQuery.all_adversarial_query.value
    query_name = "对抗机器学习"
    time_direct_zone = TimeZoneOptions.SHANGHAI.value
    filename = f"app/data/{start_date.strftime('%Y-%m-%d')}-{query_name}.md"
    print("文件名在哪里{}".format(filename))

    if choice == "1":
        query = ArticleQuery.all_adversarial_query.value
        query_name = "对抗机器学习"
    elif choice == "2":
        query = ArticleQuery.RS_adversarial_query.value
        query_name = "推荐系统的鲁棒性"
    elif choice == "3":
        query = ArticleQuery.MM_adversarial_query.value
        query_name = "多模态模型的鲁棒性"
    elif choice == "4":
        query = ArticleQuery.LLM_adversarial_query.value
        query_name = "LLMs安全"
    elif choice == "5":
        query = ArticleQuery.RS_query.value
        query_name = "推荐系统"
    elif choice == "6":
        query = ArticleQuery.MM_query.value
        query_name = "多模态学习"
    elif choice == "7":
        query = ArticleQuery.LLM_query.value
        query_name = "LLMs"
    print(f"\n您选择的查询: {query_name}")
    print(f"时间范围: {start_date.strftime('%Y年%m月%d日')} 至 {end_date.strftime('%Y年%m月%d日')}")

    # 执行搜索和翻译
    translated_papers, all_paper_titles = search_and_translate_arxiv_papers(query=query, query_name=query_name,
                                                                            start_date=start_date, end_date=end_date,
                                                                            china_tz=time_direct_zone,
                                                                            filename=filename, max_results=max_results)
    # print("搜索返回的结果{}".format(translated_papers))
    # print("搜索返回的结果2{}".format(all_paper_titles))
    # 保存结果
    if translated_papers:
        save_translated_results(translated_papers, all_paper_titles=all_paper_titles, filename=filename,
                                query_name=query_name, start_date=start_date, end_flag=True)
        print(f"\n总共处理了 {len(translated_papers)} 篇论文")
    else:
        print("\n没有找到符合条件的论文")


# 1.检索功能最顶层(检索并翻译)
def search_and_translate_arxiv_papers(query, query_name, start_date, end_date, china_tz, filename, max_results):
    # 若没有传最大篇数，则默认为100
    all_paper_titles = ""
    llm_safe_paper_list = []
    if max_results is None:
        max_results = 100
    translated_papers = []
    # 对对抗机器学习单独处理
    if query_name == "对抗机器学习":
        llm_safe_paper_list = list(extract_paper_links(
            f"{start_date.strftime('%Y-%m-%d')}-papers/{start_date.strftime('%Y-%m-%d')}-LLMs安全.md"))
        print(f"已提取 {len(llm_safe_paper_list)} 篇已存在于LLM安全列表中的论文链接")

    try:
        # 调用arxiv的api
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.LastUpdatedDate
        )

        print(f"开始搜索arXiv论文，查询: {query}")
        print(f"预计获取最多{max_results}篇论文...")

        for i, result in enumerate(search.results()):
            # print("每一次循环的结果{}".format(result))
            try:
                # 转换时间
                utc_time = result.updated
                # print("utc_time{}".format(utc_time))
                china_time = utc_time.astimezone(china_tz)
                # print("china_time{}".format(china_time))
                # print("start_date{}".format(start_date))
                # print("end_date{}".format(end_date))
                china_time_text = china_time.strftime("%Y年%m月%d日")

                # 检查时间范围
                if start_date <= china_time < end_date:
                    # print("进入了查询中")
                    if query_name == "对抗机器学习" and result.pdf_url in llm_safe_paper_list:
                        print(f"论文《 {result.title[:50]}...》已在LLM安全列表中，无需放入 对抗机器学习 目录中，跳过")
                        continue
                    print(f"\n处理第{i + 1}篇论文: {result.title[:50]}...")

                    # 翻译标题和摘要
                    translated_title = translate_text(result.title)
                    translated_summary = translate_text(result.summary)

                    # 收集作者信息
                    authors = [author.name for author in result.authors]

                    # 构建论文信息字典
                    paper_info = {
                        "date": china_time_text,
                        "entry_id": result.entry_id,
                        "pdf_url": result.pdf_url,
                        "title_en": result.title,
                        "title_zh": translated_title,
                        "authors": authors,
                        "summary_en": clean_abstract(result.summary),
                        "summary_zh": translated_summary,
                        "comment": "**Comment**: " + result.comment if result.comment else ""
                    }

                    translated_papers.append(paper_info)

                    # 打印结果
                    print(f"日期: {china_time_text}")
                    print(f"标题(EN): {result.title}")
                    print(f"标题(ZH): {translated_title}")
                    print(f"作者: {', '.join(authors[:3])}{'...' if len(authors) > 3 else ''}")
                    print(f"链接: {result.pdf_url}")
                    print("-" * 80)
                    all_paper_titles += "- " + result.title + "\n"
                    save_translated_results(papers=translated_papers, all_paper_titles=all_paper_titles,
                                            filename=filename, start_date=start_date, query_name=query_name)  # 实时保存结果
                    time.sleep(2 + random.uniform(0, 2))

            except Exception as e:
                print(f"处理论文时出错: {str(e)}, 此时i={i}")
                continue
            if i % 10 == 0 and i > 0:
                print("已处理10篇论文，休息一会儿以防止API过载...")
                time.sleep(5 + random.uniform(0, 2))

    except Exception as e:
        print(f"初始化搜索arXiv论文时出错: {str(e)}")

    return translated_papers, all_paper_titles

# 2.将英文摘要的多行文本合并成一个自然段（无手动换行）
def clean_abstract(abstract):
    """
    将英文摘要的多行文本合并成一个自然段（无手动换行）

    Args:
        abstract (str): 原始摘要文本

    Returns:
        str: 合并后的单段摘要
    """
    if not abstract:
        return ""

    # 处理不同类型的换行符，统一替换为空格
    cleaned = abstract.replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ')

    # 合并多个个空格为一个空格
    cleaned = re.sub(r'\s+', ' ', cleaned)

    # 移除首尾空格
    cleaned = cleaned.strip()

    # 确保句子之间有适当的标点和空格
    cleaned = re.sub(r'([.!?])([A-Z])', r'\1 \2', cleaned)

    # 不进行手动换行，完全交给Markdown处理
    return cleaned

# 3.翻译摘要与标题
def translate_text(text, source_lang="en", target_lang="zh", max_retries=3):
    if not text or not API_KEY:
        return text

    # 硅基流动API地址 - 尝试使用备用地址
    url = "https://api.siliconflow.cn/v1/chat/completions"
    # url = "https://api.siliconcloud.cn/v1/chat/completions"  # 备用API地址（如果有的话）
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # 构建翻译提示词
    prompt = f"""请将以下学术文本从{source_lang}翻译成{target_lang}(中文)，保持学术严谨性和专业术语的准确性：{text}，只需输出翻译的中文结果，不要添加任何额外内容。"""

    payload = {
        "model": TRANSLATION_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,  # 较低的温度以保证翻译准确性
        "max_tokens": min(2000, len(text) * 2)  # 根据原文长度动态调整
    }

    try:
        # 增加超时时间，并添加连接超时设置
        # 配置请求会话以提高性能
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
            timeout=(15, 90),  # (连接超时, 读取超时) - 进一步增加超时时间
            verify=True,
            allow_redirects=True
        )
        response.raise_for_status()

        result = response.json()
        if result and "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"].strip()
        else:
            error_msg = f"翻译API返回空结果"
            if response:
                error_msg += f": {response.text[:500]}"  # 限制输出长度
            print(error_msg)
            return text

    except requests.exceptions.Timeout as e:
        print(f"翻译API调用超时: {str(e)}")
        print("正在重试...")
        raise  # 重新抛出异常以触发重试机制

    except requests.exceptions.ConnectionError as e:
        print(f"翻译API连接错误: {str(e)}")
        print("请检查网络连接和API地址")
        print("正在重试...")
        raise  # 重新抛出异常以触发重试机制

    except requests.exceptions.HTTPError as e:
        print(f"翻译API HTTP错误: {str(e)}")
        # 在HTTPError中，response变量可能不存在，需要安全访问
        if 'response' in locals() and response is not None:
            print(f"API状态码: {response.status_code}")
            print(f"API响应: {response.text[:500]}")  # 限制输出长度

            # 处理特定的HTTP错误
            if response.status_code == 401:
                print("错误: API密钥无效或未授权")
            elif response.status_code == 429:
                print("错误: 请求过于频繁，请稍后再试")
            elif response.status_code == 503:
                print("错误: 服务暂时不可用")
            else:
                print("无法获取详细的错误信息")
        return text

    except Exception as e:
        print(f"翻译API调用发生未知错误: {str(e)}")
        return text


# 4.保存翻译结果为md文件
def save_translated_results(papers, all_paper_titles,
                            filename, query_name=None, start_date=None,
                            end_flag=False):
    if not papers or len(papers) == 0:
        print("没有可保存的论文数据")
        return

    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# Arxiv每日签[25-{start_date.strftime('%m-%d')}] | {query_name}({len(papers)}篇)\n")
            if end_flag:
                summary_text = generate_papers_summary(all_paper_titles)
                f.write(
                    f"> {start_date.strftime('%m月%d日')}共有{len(papers)}篇关于{query_name}的论文，分别围绕{summary_text}\n\n")
            f.write(f"## 今日论文标题目录\n")
            f.write(all_paper_titles + "\n\n")

            for i, paper in enumerate(papers, 1):
                f.write(f"## {i}. {paper['title_zh']}\n")
                f.write(f"**英文标题**: {paper['title_en']}\n\n")
                # f.write(f"**发表日期**: {paper['date']}\n")
                f.write(f"**作者**: {', '.join(paper['authors'])}\n\n")
                f.write(f"{paper['comment']}\n\n")
                f.write(f"**链接**: [{paper['pdf_url']}]({paper['pdf_url']})\n\n")

                f.write(f"### 摘要 (中文)\n")
                f.write(f"{paper['summary_zh']}\n\n")

                f.write(f"### 摘要 (英文)\n")
                f.write(f"{paper['summary_en']}\n\n")

                f.write("---\n\n")

        print(f"翻译结果已保存到: {filename}")

    except Exception as e:
        print(f"保存翻译结果时出错: {str(e)}")

# 5.生成论文总结
def generate_papers_summary(all_paper_titles):
    if not all_paper_titles:
        return "没有可用的论文数据进行总结"

    # 构建总结提示词
    titles = all_paper_titles
    prompt = f"""请基于以下arXiv论文标题，生成一个简洁的中文总结，文本长度不超过200字，涵盖主要研究方向和趋势：\n{titles}\n只需输出总结内容，不要添加任何额外内容。"""

    summary = call_llm_api(
        prompt=prompt,
        output_type=LLMOutputType.SUMMARIZATION,
        temperature=0.3
    )

    return summary