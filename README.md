# 站室绩效考核系统KPI-PA

Grass-roots unit performance appraisal system (KPI-PA).

- GRU-PA 站室绩效考核系统KPI-PA

    ![GRU-PA ver](https://img.shields.io/badge/ver-0.7.704-blue.svg)
    ![GRU-PA updated](https://img.shields.io/badge/updated-25/07/24%2014:29-orange.svg)
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

1. 下载并安装[Python](https://www.python.org/)(3.9<=版本<3.13)
2. 下载并安装[MySQL](https://dev.mysql.com/downloads/mysql/)(>=8.4.5)
3. 下载并编译安装[Dlib](https://github.com/davisking/dlib)(==20.0.0, 安装VS build tools后手工编译, 编译方法在documents目录中, 推荐GPU加速)
4. 克隆仓库到本地或者解压提供的源代码包
5. 配置环境变量, 将Python和Streamlit的安装路径添加到环境变量中
6. 安装依赖
    - 主要依赖
      - Streamlit # 前端框架
      - Streamlit-antd-components/extras/keyup # 前端组件库
      - Streamlit_condition_tree # 条件树SQL语句生成
      - Pycryptodome # 数据加密模块
      - NumPY # 数学计算
      - Plotly # 数据可视化
      - Python-docx # Word文档操作
      - Openpyxl/XlsxWriter # Excel文档操作
      - PyJWT # JSON Web Token认证(和风天气API需要使用)
      - Dlib # 人脸识别库(可选)
      - Face-recognition # 人脸识别(可选)
      - Opencv-python # 图像处理(可选)
      - streamlit-webrtc # 浏览器webrtc模块(可选)
      - ...

      ![Python](https://img.shields.io/badge/Python-3.12.6-blue.svg)
      ![MySQL](https://img.shields.io/badge/MySQL-8.4.5-blue.svg)
      ![Streamlit](https://img.shields.io/badge/Streamlit-1.47.0-blue.svg)
      ![Streamlit-antd-components](https://img.shields.io/badge/Streamlit_antd_components-0.3.2-blue.svg)
      ![NumPY](https://img.shields.io/badge/NumPY-2.2.6-blue.svg)
      ![Pandas](https://img.shields.io/badge/Pandas-2.3.1-blue.svg)
      ![Plotly](https://img.shields.io/badge/Plotly-6.2.0-blue.svg)
      ![Python-docx](https://img.shields.io/badge/Python_docx-1.2.0-blue.svg)
      ![Openpyxl](https://img.shields.io/badge/Openpyxl-3.1.5-blue.svg)
      ![XlsxWriter](https://img.shields.io/badge/XlsxWriter-3.2.5-blue.svg)
      ![PyJWT](https://img.shields.io/badge/PyJWT-2.10.1-blue.svg)
      ![Dlib](https://img.shields.io/badge/Dlib-20.0.0-blue.svg)
      ![Face-recognition](https://img.shields.io/badge/Face_recognition-1.3.0-blue.svg)
      ![Opencv-python](https://img.shields.io/badge/Opencv_python-4.12.0.88-blue.svg)
      ![Streamlit-webrtc](https://img.shields.io/badge/Streamlit_webrtc-0.63.3-blue.svg)

    - 或使用提供的requirements.txt文件自动安装
      - `pip install -r requirements.txt`
7. 运行程序
    - a. 打开命令行工具cmd或Cmder
    - b. 进入程序目录
    - c. 运行
      - `streamlit run gru-pa.py`
8. 访问地址
    - 本机运行, 请访问`http://localhost:8510` (端口可使用--server.port参数自行修改)
    - 服务器运行，请访问`http://域名:8510` (具体域名请询问管理员)

## Construction

- .streamlit/config.toml # Streamlit配置文件, 默认端口8510([修改前请查阅相关文档](https://docs.streamlit.io/develop/api-reference/configuration/config.toml))
- .mysql.cnf # MySQL配置文件
- gru-pa.py # 入口文件及主程序 All in one
- mysql_pool.py # MySQL连接池模块(不同步)
- commFunc.py # 公共函数模块
- gen_badges.py # 徽章生成模块
- face_login.py # 人脸登录模块
- hf_weather.py # 和风天气API模块
- gd_weather.py # 高德天气API模块
- dlib # dlib人脸识别库whl文件、编译说明及68个点模型文件
- documents # 文档文件(不同步)
- ID_Photos # 用户人脸图像, 用于生成识别数据
- Images # 图片文件
  - badges # 徽章文件
  - Clock-Images # 时钟图片
  - logos # logo文件
- MyComponentsScript # 自定义组件脚本, txt格式, 系统自动转换
- MySQL_Backup # MySQL备份文件
- user_pa # 用户导出文档
- README.md # 项目说明文件(本文件, Markdown格式)
- CHANGELOG.md # 项目更新日志
- requirements.txt # 自动安装依赖文件
- CSC-Common-CustomDict.txt # CSpell自定义通用字典文件
- CSC-Project-CustomDict.txt # CSpell自定义字典文件
- DBBackup.ps1 # 数据库备份PS脚本
- restoredb.bat # 数据库恢复bat脚本

## Functions

- 工作量批量和手工录入
- 工作减分项录入
- 记录修改
- 统计查询及导出
- 趋势图
- 数据检查与审核
- 高级查询
- 人脸图片提交及验证
- 历史天气
- 公告发布
- 数据库操作及备份

## Features

- 采用多种技术简化用户工作量
- 人脸识别登录

## Git Repository

[GRU-PA 站室绩效考核系统KPI-PA](https://github.com/simonpek88/GRU-PA.git)

## License

![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)

MIT © 2025 Simon Lau TradeMark :rainbow[Enjoy for AP] ™
