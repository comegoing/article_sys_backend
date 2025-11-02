"""
该文件为文献检索后端接口的功能实现层
"""
import re
import time

import arxiv
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.service.TranslateUtils import translate_by_python
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
    # filename = f"app/data/{start_date.strftime('%Y-%m-%d')}-{query_name}.md"

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

    # 执行搜索和翻译
    translated_papers = search_and_translate_arxiv_papers(query=query,
                                                          start_date=start_date, end_date=end_date,
                                                          china_tz=time_direct_zone,
                                                          max_results=max_results)

    rsp_data = []

    # 对搜索结果进行处理
    if translated_papers:

        for i, paper in enumerate(translated_papers, 1):
            temp_data = {
                'titleZH': paper['titleZH'],
                'titleEN': paper['titleEN'],
                'author': paper['author'],
                'url': paper['url'],
                'abstractZH': paper['abstractZH'],
                'abstractEN': paper['abstractEN'],
                'date': paper['date'],
                'detailVisible': False,
                'detailChecked': False,

            }
            rsp_data.append(temp_data)
    else:
        print("\n没有找到符合条件的论文")

    return rsp_data


# 1.检索功能最顶层(检索并翻译)
def search_and_translate_arxiv_papers(query, start_date, end_date, china_tz, max_results):
    # 若没有传最大篇数，则默认为10
    if max_results is None:
        max_results = 10
    translated_papers = []

    try:
        # 调用arxiv的api
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.LastUpdatedDate
        )

        print(f"开始搜索arXiv论文，查询: {query}")

        for i, result in enumerate(search.results()):
            try:
                # 转换时间
                utc_time = result.updated
                china_time = utc_time.astimezone(china_tz)
                china_time_text = china_time.strftime("%Y年%m月%d日")

                # 翻译标题和摘要
                translated_title = translate_by_python(result.title, 'en', 'zh')
                abstract_en = clean_abstract(result.summary)
                translated_summary = translate_by_python(abstract_en, 'en', 'zh')

                # 收集作者信息
                authors = [author.name for author in result.authors]

                # 构建论文信息字典
                paper_info = {
                    "entryID": result.entry_id,
                    "date": china_time_text,
                    "url": result.pdf_url,
                    "titleEN": result.title,
                    "titleZH": translated_title,
                    "author": ', '.join(authors),
                    "abstractEN": abstract_en,
                    "abstractZH": translated_summary
                }

                translated_papers.append(paper_info)

                # 打印结果
                print(f"日期: {china_time_text}")
                print(f"标题(EN): {result.title}")
                print(f"标题(ZH): {translated_title}")
                print(f"作者: {', '.join(authors)}")
                print(f"链接: {result.pdf_url}")
                print(f"摘要(EN): {abstract_en}")
                print(f"摘要(ZH): {translated_summary}")
                print("-" * 80)

            except Exception as e:
                print(f"处理论文时出错: {str(e)}, 此时i={i}")
                continue
            finally:
                if i % 10 == 0 and i > 0:
                    print("已处理10篇论文，休息一会儿以防止API过载...")
                    time.sleep(5)

    except Exception as e:
        print(f"初始化搜索arXiv论文时出错: {str(e)}")

    return translated_papers


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
