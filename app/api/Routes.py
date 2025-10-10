"""
此文件用于定义接口供前端调用
"""
import datetime

from flask import Flask

from app.service.ArxivTranslator import arxivTranslate
from app.utils.Constant import TimeZoneOptions

# flask基础服务
app = Flask(__name__)

# =================== 以下为flask后端接口 =========================
# 初始页面接口
@app.route('/')
def origin():
    return '这是接口测试'

# 检索文献接口
@app.route('/api/ArxivTranslator', methods=['GET'])
def arxivTranslator():
    china_tz = TimeZoneOptions.SHANGHAI.value
    start_date = datetime.datetime(2025, 10, 9, tzinfo=china_tz)
    # end_date是start_date的后一天
    end_date = start_date + datetime.timedelta(days=1)
    arxivTranslate(start_date, end_date, "1",300)
    return '这是接口测试'
