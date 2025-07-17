# 站室绩效考核系统KPI-PA

Grass-roots unit performance appraisal system (KPI-PA).

- GRU-PA 站室绩效考核系统KPI-PA

    ![GRU-PA ver](https://img.shields.io/badge/ver-0.4.434-blue.svg)
    ![GRU-PA updated](https://img.shields.io/badge/updated-2025/07/17%2010:37-orange.svg)
    ![GRU-PA build](https://img.shields.io/badge/build-passing-green.svg)

## 站室绩效考核系统KPI-PA 是一个前端基于 Streamlit 框架，后端基于Python数据处理的web应用，旨在简化站室工作量录入、统计及考核

## Contents

-
  - [安装](#install)
  - [项目结构](#construction)
  - [功能](#functions)
  - [特色](#features)
  - [Git-Repository](#git-repository)
  - [License](#license)

## Install

1. 下载并安装[Python](https://www.python.org/)(3.9<=版本<=3.13)
2. 下载并安装[MySQL](https://dev.mysql.com/downloads/mysql/)(8.4.5)
3. 克隆仓库到本地或者解压提供的源代码包
4. 配置环境变量, 将Python和Streamlit的安装路径添加到环境变量中
5. 安装依赖
    - 手工安装
      - MySQL # 数据库
      - Streamlit # 前端框架
      - streamlit-antd-components/extras/keyup # 前端组件库
      - streamlit_condition_tree # 条件树SQL语句生成
      - pycryptodome # 数据加密模块
      - plotly # 数据可视化
      - python-docx # Word文档操作
      - openpyxl/XlsxWriter # Excel文档操作
      - PyJWT # JSON Web Token认证
      - ...

      ![Python](https://img.shields.io/badge/Python-3.12.6-blue.svg)
      ![MySQL](https://img.shields.io/badge/MySQL-8.4.5-blue.svg)
      ![Streamlit](https://img.shields.io/badge/Streamlit-1.46.1-blue.svg)
      ![NumPY](https://img.shields.io/badge/NumPY-1.26.4-blue.svg)
      ![Pandas](https://img.shields.io/badge/Pandas-2.3.0-blue.svg)
      ![Plotly](https://img.shields.io/badge/Plotly-6.2.0-blue.svg)
      ![Python-docx](https://img.shields.io/badge/Python_docx-1.2.0-blue.svg)
      ![Openpyxl](https://img.shields.io/badge/Openpyxl-3.1.5-blue.svg)
      ![XlsxWriter](https://img.shields.io/badge/XlsxWriter-3.2.5-blue.svg)
      ![PyJWT](https://img.shields.io/badge/PyJWT-2.10.1-blue.svg)

    - 或使用提供的requirements.txt文件自动安装
      - `pip install -r requirements.txt`
6. 运行程序
    - a. 打开命令行工具cmd或Cmder
    - b. 进入程序目录
    - c. 运行
      - `streamlit run gru-pa.py --server.port 8510`
7. 访问地址
    - 本机运行, 请访问`http://localhost:8510` (端口可使用--server.port参数自行修改)
    - 服务器运行，请访问`http://域名:8510` (具体域名请询问管理员)

## Construction

- .streamlit # Streamlit配置文件, 默认端口8501([修改前请查阅相关文档](https://docs.streamlit.io/develop/api-reference/configuration/config.toml))
- gru-pa.py # 入口文件及主程序 All in one
- commFunc.py # 公共函数
- gen_badges.py # 徽章生成
- hf_weather.py # 和风天气API
- gd_weather.py # 高德天气API
- MyComponentsScript # 自定义组件脚本
- css # css样式文件
- js # js脚本文件
- README.md # 项目说明文件(本文件, Markdown格式)
- requirements.txt # 自动安装依赖文件
- CSC-Project-CustomDict.txt # CSpell自定义字典文件
- DBBackup.ps1 # 数据库备份PS脚本
- restoredb.bat # 数据库恢复bat脚本
- 其他各种导出导入文件目录

## Functions

- 工作量批量和手工录入
- 工作减分项录入
- 记录修改
- 统计查询及导出
- 趋势图
- 数据检查与审核
- 高级查询
- 历史天气
- 公告发布
- 数据库操作(ID重置及批量更新固定分数项)

## Features

- 采用多种技术简化用户工作量

## Git Repository

[GRU-PA 站室绩效考核系统KPI-PA](https://github.com/simonpek88/GRU-PA.git)

## License

![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)

MIT © 2024-2027 Simon Lau TradeMark :rainbow[Enjoy for AP] ™
