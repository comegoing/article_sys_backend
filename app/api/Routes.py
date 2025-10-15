"""
此文件用于定义接口供前端调用
"""
import datetime

from flask import Flask, request, jsonify

from app.service.ArxivTranslator import arxivTranslate
from app.utils.Constant import TimeZoneOptions
from flask_cors import CORS
# flask基础服务
app = Flask(__name__)
# 启用 CORS，允许所有域名访问
CORS(app)

# =================== 以下为flask后端接口 =========================
# 初始页面接口
@app.route('/')
def origin():
    return '这是接口测试'


# 检索文献接口
@app.route('/api/ArxivTranslator', methods=['POST'])
def arxivTranslator():
    try:
        # 获取请求中的JSON数据
        data = request.get_json()
        print(f"接收到的请求数据: {data}")  # 调试日志

        # 如果客户端没有发送JSON数据，使用默认值
        if data is None:
            data = {}

        # 从请求数据中获取参数，如果没有提供则使用默认值
        start_date_str = data.get('start_date', '2025-10-09')
        days = data.get('days', 1)
        category = data.get('category', '1')
        max_results = data.get('max_results', 5)

        print(f"解析参数: start_date={start_date_str}, days={days}, category={category}, max_results={max_results}")

        # 解析日期
        china_tz = TimeZoneOptions.SHANGHAI.value
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').replace(tzinfo=china_tz)
        end_date = start_date + datetime.timedelta(days=days)

        print(f"计算后的日期范围: {start_date} 到 {end_date}")

        # 调用你的函数
        print("开始调用 arxivTranslate 函数...")
        result = arxivTranslate(start_date, end_date, category, max_results)
        print("arxivTranslate 函数调用完成")

        # 返回JSON响应
        response = {
            "status": "success",
            "message": "文献检索和翻译完成",
            "parameters": {
                "start_date": start_date_str,
                "days": days,
                "category": category,
                "max_results": max_results
            },
            "data": result
        }
        print(f"返回响应: {response}")

        return jsonify(response)

    except Exception as e:
        # 打印详细的错误信息
        error_traceback = traceback.format_exc()
        print(f"发生错误: {str(e)}")
        print(f"错误堆栈: {error_traceback}")

        # 如果发生错误，返回错误信息
        return jsonify({
            "status": "error",
            "message": str(e),
            "traceback": error_traceback  # 在生产环境中应该移除这一行
        }), 500
