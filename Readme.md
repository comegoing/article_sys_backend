# 1.项目结构
```
article_sys_backend/
├── app
│   ├── api
│   │   └── Routes.py
│   ├── data
│   ├── service
│   │   ├── ArxivTranslator.py
│   │   ├── ExtractPaperLinks.py
│   │   └── LLM.py
│   └── utils
│       ├── Config.py
│       └── Constant.py
└── run.py
```
# 2.文件说明
run.py - 项目启动文件(启动入口)
utils/* - 配置常量等工具文件  
service/* - 功能层(实际功能实现文件)  
api/Routes.py - api层(提供后端接口)  
data/* - 文件存放  

# 3.项目规范
--文件名使用大驼峰 (ArxivTranslator 如部分名词无法使用大驼峰，则可以全大写，例如LLM,CNN)  
--变量名使用小驼峰或下划线 arxivTranslator arxiv_translator  
--常量使用全大写 TRANSLATION DEEP_SEEK  