"""
该文件为文从生成文档中提取论文链接的功能实现层
"""
import re
from typing import Set


# 该方法用于从生成文档中提取论文链接
def extract_paper_links(filename: str) -> Set[str]:
    """
    从Markdown文档中提取所有论文的链接
    
    Args:
        filename: Markdown文档的路径
        
    Returns:
        包含所有论文链接的集合
    """
    # 用于匹配Markdown链接的正则表达式
    # 匹配格式：[显示文本](链接)
    link_pattern = r'\[.*?\]\((.*?)\)'

    # 用于匹配以"链接:"开头的行（可能包含粗体标记）
    link_line_pattern = r'^\s*\*\*?链接\*\*?\s*:\s*'

    links = set()

    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                # 检查是否是包含链接的行
                if re.search(link_line_pattern, line):
                    # 提取链接
                    matches = re.findall(link_pattern, line)
                    for match in matches:
                        link = match.strip()
                        # 确保链接是有效的URL
                        if link.startswith(('http://', 'https://')):
                            links.add(link)
    except FileNotFoundError:
        print(f"错误：文件 '{filename}' 未找到")
    except Exception as e:
        print(f"处理文件时发生错误：{e}")

    return links

if __name__ == "__main__":
    paper_links = extract_paper_links('2025-10-06-papers/2025-10-06-LLMs安全.md')
    print(f"提取到 {len(paper_links)} 个唯一的论文链接:")
    for link in paper_links:
        print(link)
