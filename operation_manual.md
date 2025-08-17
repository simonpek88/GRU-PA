# GRU-PA 站室绩效考核系统完整操作手册

-
    ![Support Ukraine](https://img.shields.io/badge/support-Ukraine-yellow?labelColor=005bbb&color=ffd500&style=flat.svg)
    ![GRU-PA ver](https://img.shields.io/badge/ver-0.13.1352-blue.svg)
    ![GRU-PA updated](https://img.shields.io/badge/updated-25/08/11%2016:59-orange.svg)
    ![GRU-PA build](https://img.shields.io/badge/build-passing-deepgreen.svg)
    ![GRU-PA languages-count](https://img.shields.io/github/languages/count/simonpek88/GRU-PA.svg)
    ![GRU-PA commits](https://img.shields.io/github/commit-activity/t/simonpek88/GRU-PA.svg)

## 目录

- [0.Todo](#todo)
- [1.系统概述](#系统概述)
- [2.系统安装与配置](#系统安装与配置)
- [3.快速入门](#快速入门)
- [4.用户管理](#用户管理)
- [5.工作量管理](#工作量管理)
- [6.数据统计分析](#数据统计分析)
- [7.值班数据统计及导出](#值班数据统计及导出)
- [8.公告发布和修改](#公告发布和修改)
- [9.人脸识别系统](#人脸识别系统)
- [10.天气功能](#天气功能)
- [11.数据导出](#数据导出)
- [12.系统管理](#系统管理)
- [13.数据库操作](#数据库操作)
- [14.故障排除](#故障排除)
- [15.安全指南](#安全指南)
- [16.技术支持](#技术支持)

## Todo

- 统计导出自定义模板
- 人脸识别最大尝试次数
- 系统会话超时
- 用户密码定期修改
- 用户修改密码不能重复使用最近5次密码
- 登录连续5次失败则锁定30分钟
- 基于IP的白名单的访问控制
- 审计所有敏感操作

<a id="系统概述"></a>

## 系统概述

### 🎯 系统定位

GRU-PA (Grass-roots unit Performance Appraisal system) 是一款专为基层站室设计的绩效考核管理系统，集成了工作量录入、统计分析、人脸识别、天气查询等现代化管理功能。

### 🏗️ 技术架构

- 前端框架 : Streamlit 1.48.0
- 后端语言 : Python 3.9-3.12
- 数据库 : MySQL 8.4.5 LTS
- 人脸识别 : Dlib 20.0.0 + OpenCV 4.12
- 图表可视化 : Plotly 6.2.0 + Nivo
- 文档处理 : python-docx 1.2.0 + openpyxl 3.1.5

### ✨ 核心特性

- 双因子认证 : 密码 + 人脸识别双重验证
- 智能录入 : 支持批量录入、手工录入, 智能推荐工作内容
- 多维分析 : 9种图表类型，支持时间序列分析
- 实时天气 : 集成和风天气和高德天气API，支持历史天气和高温记录查询
- 一键导出 : Excel/Word双格式，支持自定义模板
- 权限管控 : 基于RBAC的精细化权限管理

<a id="系统安装与配置"></a>

## 系统安装与配置

### 🖥️ 系统要求

#### 服务器硬件要求

<div style="overflow-x: auto;">

| 组件 | 最低配置 | 推荐配置 |
|:-----|:---------|:---------|
| **CPU** | <span style="color: #e74c3c;">Intel i5 4代</span> | <span style="color: #27ae60;">Intel i7 12代或AMD Ryzen7 7代</span> |
| **显卡** | <span style="color: #e74c3c;">集成显卡</span> | <span style="color: #27ae60;">GeForce GTX 2080 Ti</span> |
| **内存** | <span style="color: #e74c3c;">8GB DDR3</span> | <span style="color: #27ae60;">16GB DDR5</span> |
| **存储** | <span style="color: #e74c3c;">64GB HDD</span> | <span style="color: #27ae60;">128GB SSD</span> |
| **网络** | <span style="color: #e74c3c;">100Mbps</span> | <span style="color: #27ae60;">1000Mbps</span> |
| **摄像头** | <span style="color: #e74c3c;">1080p</span> | <span style="color: #27ae60;">1080p</span> |

</div>

> 💡 **配置建议**:

- 最低配置可满足基本运行需求
- 推荐配置可获得更流畅的用户体验，特别是人脸识别功能
- 人脸识别功能对摄像头和CPU要求较高，建议采用推荐配置

#### 软件环境

<div style="overflow-x: auto;">

| 软件 | 版本要求 | 下载地址 |
|:-----|:---------|:---------|
| **Python** | `3.9-3.12.6` | [Python官网](https://www.python.org) <span style="font-size: 0.85em;">🔗</span> |
| **MySQL** | `8.4.5 LTS` | [MySQL官网](https://dev.mysql.com) <span style="font-size: 0.85em;">🔗</span> |
| **Git** | `2.30+` | [Git官网](https://git-scm.com) <span style="font-size: 0.85em;">🔗</span> |
| **Visual Studio Build Tools** | `2019+` <br>_(Windows编译dlib用)_ | [Microsoft VS官网](https://visualstudio.microsoft.com/zh-hans/downloads/) <span style="font-size: 0.85em;">🔗</span> |

</div>

> 💡 **安装提示**:

- Python安装时请勾选"Add Python to PATH"选项
- Windows系统需要安装Visual Studio Build Tools以编译Dlib库
- 建议使用LTS版本以确保系统稳定性

### 🚀 安装步骤

1. 环境准备

    ```bash
    # Windows系统
    # 安装Python时勾选"Add Python to PATH"
    # 安装MySQL时记住root密码

    # Linux系统 (Ubuntu/Debian)
    sudo apt update && sudo apt upgrade -y
    sudo apt install python3.12 python3-pip mysql-server-8.4 git build-essential cmake
    ```

2. 获取源代码

    ```bash
    # 方法1: Git克隆
    git clone https://github.com/simonpek88/GRU-PA.git
    cd GRU-PA

    # 方法2: 直接下载
    # 从GitHub Releases下载最新版本ZIP包
    ```

3. 安装依赖

    - 主要依赖
    <style>
    .dependency-list {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 15px;
        margin-top: 10px;
    }
    .dependency-item {
        background: #f8f9fa;
        border-left: 4px solid #3498db;
        padding: 12px 15px;
        border-radius: 0 8px 8px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    .dependency-item:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        background: #e9f7fe;
    }
    .dependency-name {
        font-weight: 600;
        color: #2c3e50;
        font-family: 'Courier New', monospace;
    }
    .dependency-desc {
        color: #6c757d;
        font-size: 1em;
        margin-top: 5px;
    }
    .optional {
        border-left-color: #23d5e1ff;
    }
    .optional .dependency-name {
        color: #2c3e50;
    }
    /* 清除浮动影响 */
    .dependency-clear {
        clear: both;
        height: 1px;
        overflow: hidden;
        margin: 0;
        padding: 0;
    }
    </style>

    <div class="dependency-list">
        <div class="dependency-item">
        <div class="dependency-name">Streamlit</div>
        <div class="dependency-desc">前端框架</div>
        </div>
        <div class="dependency-item">
        <div class="dependency-name">Streamlit-antd-components/extras/search</div>
        <div class="dependency-desc">前端组件库</div>
        </div>
        <div class="dependency-item">
        <div class="dependency-name">Streamlit_condition_tree</div>
        <div class="dependency-desc">条件树SQL语句生成</div>
        </div>
        <div class="dependency-item">
        <div class="dependency-name">Pycryptodome</div>
        <div class="dependency-desc">数据加密模块</div>
        </div>
        <div class="dependency-item">
        <div class="dependency-name">NumPY</div>
        <div class="dependency-desc">数学计算</div>
        </div>
        <div class="dependency-item">
        <div class="dependency-name">Plotly</div>
        <div class="dependency-desc">数据可视化</div>
        </div>
        <div class="dependency-item">
        <div class="dependency-name">Nivo</div>
        <div class="dependency-desc">数据可视化</div>
        </div>
        <div class="dependency-item">
        <div class="dependency-name">Python-docx</div>
        <div class="dependency-desc">Word文档操作</div>
        </div>
        <div class="dependency-item">
        <div class="dependency-name">Openpyxl/XlsxWriter</div>
        <div class="dependency-desc">Excel文档操作</div>
        </div>
        <div class="dependency-item">
        <div class="dependency-name">PyJWT</div>
        <div class="dependency-desc">JSON Web Token认证 (和风天气API使用)</div>
        </div>
        <div class="dependency-item optional">
        <div class="dependency-name">Dlib</div>
        <div class="dependency-desc">人脸识别库 (可选)</div>
        </div>
        <div class="dependency-item optional">
        <div class="dependency-name">Face-recognition</div>
        <div class="dependency-desc">人脸识别 (可选)</div>
        </div>
        <div class="dependency-item optional">
        <div class="dependency-name">Opencv-python</div>
        <div class="dependency-desc">图像处理 (可选)</div>
        </div>
        <div class="dependency-item optional">
        <div class="dependency-name">streamlit-webrtc</div>
        <div class="dependency-desc">浏览器webrtc模块 (可选)</div>
        </div>
    </div>
    <div class="dependency-clear"></div>

      ![Python](https://img.shields.io/badge/Python-3.12.6-blue.svg)
      ![MySQL](https://img.shields.io/badge/MySQL-8.4.5-blue.svg)
      ![Streamlit](https://img.shields.io/badge/Streamlit-1.47.1-blue.svg)
      ![Streamlit-antd-components](https://img.shields.io/badge/Streamlit_antd_components-0.3.2-blue.svg)
      ![NumPY](https://img.shields.io/badge/NumPY-2.3.2-blue.svg)
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

    ```bash
    # 创建虚拟环境 (推荐)
    python -m venv gru-pa-env
    source gru-pa-env/bin/activate  #Linux/Mac
    # 或
    gru-pa-env\Scripts\activate     #Windows

    # 安装Python包
    pip install -r requirements.txt

    # 安装Dlib (Windows 请对应python版本选择对应的whl文件)
    pip install dlib/dlib-20.0.0-cp{python版本}-cp{python版本}-win_amd64.whl

    # 安装Dlib (Windows/Linux/Mac编译)
    cd dlib
    mkdir build
    cd build
    cmake .. -DDLIB_USE_CUDA=1 -DUSE_AVX_INSTRUCTIONS=1  # GPU加速
    # 或者
    cmake .. # 无GPU环境
    cmake --build .
    cd ..
    # setup.py 安装
    python setup.py install
    # 或者
    # 编译成wheel文件安装 (推荐)
    python setup.py bdist_wheel # 生成wheel文件
    pip install dist/dlib-20.0.0-cp{python版本}-cp{python版本}-win_amd64.whl
    ```

    ```bash
    # 验证GPU加速是否正常
    python
    import dlib
    print(dlib.DLIB_USE_CUDA)
    ```

4. 数据库配置

    ```bash
    -- 登录MySQL
    mysql -u root -p

    -- 创建数据库
    CREATE DATABASE gru_pa DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

    -- 创建用户并授权
    CREATE USER 'gru_pa_user'@'localhost' IDENTIFIED BY 'your_secure_password';
    GRANT ALL PRIVILEGES ON gru_pa.* TO 'gru_pa_user'@'localhost';
    FLUSH PRIVILEGES;

    -- 导入初始数据
    mysql -u gru_pa_user -p gru_pa < MySQL_Backup/GRU-PA-MySQL_Backup_{时间戳}.sql

    -- 创建.mysql.cnf (推荐)
    [client]
    user = {username}
    password = {password}
    port = {port}
    ```

5. 配置文件设置

    默认端口8510 [修改前请查阅相关文档](https://docs.streamlit.io/develop/api-reference/configuration/config.toml)

    ```bash
    # .streamlit/config.toml
    [server]
    port = 8510
    address = "localhost"
    enableCORS = true # 允许跨域

    [browser]
    gatherUsageStats = false
    ```

### 🏁 启动系统

#### 开发环境

```bash
# 直接启动
streamlit run gru-pa.py

# 指定参数启动
streamlit run gru-pa.py --server.port {空闲端口} --server.address localhost或服务器IP地址
```

#### 生产环境

```bash
# 使用screen保持后台运行 (Linux)
screen -S gru-pa
streamlit run gru-pa.py --server.port {空闲端口} --server.address localhost或服务器IP地址 --server.headless true
# 按Ctrl+A+D退出screen

# 使用systemd服务 (Linux)
sudo cp gru-pa.service /etc/systemd/system/
sudo systemctl enable gru-pa
sudo systemctl start gru-pa

# Windows后台运行
streamlit run gru-pa.py (默认配置)
# 或
streamlit run gru-pa.py --server.port {空闲端口} --server.address localhost或服务器IP地址 --server.headless true
```

<a id="快速入门"></a>

## 快速入门

### 🎯 首次使用流程

#### 1. 管理员初始化

首次使用系统时，请使用默认管理员账户登录，登录后应立即修改默认密码。

```bash
# 访问系统地址并使用管理员账户登录
# 站点: 北京站
```

#### 基础配置

1. 创建站点 : 系统设置 → 站点管理
2. 添加用户 : 用户管理 → 添加用户
3. 设置工作内容 : 基础数据 → 工作内容管理
4. 配置权限 : 权限管理 → 角色权限设置

#### 初次登录流程

1. 访问系统 : <http://localhost:8510>
2. 选择站点 : 选择所属站点
3. 用户登录 : 选择用户名，输入密码
4. 首次登录 : 系统强制修改初始密码
5. 人脸录入 : 设置 → 录入人脸数据

<a id="用户管理"></a>

## 用户管理

### 👥 用户角色体系

<div style="overflow-x: auto;">

| 角色 | 权限范围 | 典型用户 |
|:-----|:---------|:---------|
| **👑 超级管理员** | <span style="color: #2980b9;">全系统管理</span> | DBA管理员 |
| **🏢 站点管理员** | <span style="color: #27ae60;">站点内管理</span> | 站长 |
| **👤 普通员工** | <span style="color: #f39c12;">个人操作</span> | 一般员工 |
| **🔎 访客** | <span style="color: #95a5a6;">只读权限</span> | 临时用户 |

</div>

> 💡 **角色说明**:

- 超级管理员拥有系统最高权限，可管理所有站点和用户
- 站点管理员负责单个站点的日常管理
- 普通员工可进行个人工作量录入和查询
- 访客仅可查看公开信息，无编辑权限

### 📝 用户操作指南

- 修改密码 : 账户 → 密码修改
- 找回密码 : 联系管理员重置
- 密码策略 : 4-20位，包含大小写+数字+特殊字符 (建议)
- 定期更新 : 建议90天更换一次密码
- 个人信息维护 (建议)
  - 基本信息 : 姓名、部门
  - 工作信息 : 工号、入职时间、岗位
  - 个人设置 : 主题偏好、默认设置

<a id="工作量管理"></a>

## 工作量管理

### 📊 工作量录入系统

#### 批量录入 - 智能模式

操作路径: 功能 → 工作量批量录入

1. **日期选择**
   - 默认: 昨日日期
   - 范围: 当日日期之前

2. **工作内容选择**
   - 搜索框: 支持模糊搜索
   - 分类显示: 按工作类型分组
   - 收藏夹: 常用工作快速选择
   - 默认工作: 默认工作自动勾选

3. **分值设置**
   - 自动匹配: 根据工作内容自动加载分值
   - 手动调整: 可修改系统建议分值
   - 批量设置: 统一设置相同分值
   - 范围限制: 1-100分，步长1

4. **智能推荐**
   - 基于历史: 推荐相似日期的工作
   - 基于岗位: 推荐岗位相关的工作
   - 基于习惯: 学习个人工作习惯

#### 手工录入 - 精准模式

#### 减分项录入

操作路径: 功能 → 工作减分项录入

减分项类型:

- 工作失误: -100至-50分 (按程度)
- 多次同类型失误: -300至-100分 (按次数)

录入要求:

- 必须选择减分项类型
- 填写具体原因
- 上传证明材料 (可选)
- 管理员录入后直接生效

### 📈 数据审核流程

#### 审核状态

- 待审核 : 刚提交，等待审核
- 已通过 : 审核通过，计入统计
- 已退回 : 审核不通过，需修改
- 已修改 : 修改后重新提交

#### 审核权限

- 本人 : 只能查看，不能审核
- 站长 : 可审核全站人员
- 管理员 : 可审核所有记录

<a id="数据统计分析"></a>

### 数据统计分析

### 📊 统计维度

#### 时间维度

- 日报 : 每日工作量明细
- 月报 : 本月趋势分析
- 任意时间段 : 工作统计

#### 人员维度

- 个人 : 个人工作轨迹
- 站点 : 站点整体情况
- 公司 : 多站点汇总

#### 工作维度

- 工作类型 : 各类工作占比
- 分值分布 : 高分/低分工作识别
- 效率分析 : 单位时间工作量
- 质量评估 : 工作质量评分

### 📈 图表系统 - 9种图表类型详解

<style>
.chart-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin: 20px 0;
}
.chart-card {
  border: 1px solid #e1e8ed;
  border-radius: 10px;
  padding: 15px;
  background: #fff;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
  transition: all 0.3s ease;
}
.chart-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}
.chart-header {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}
.chart-number {
  background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
  color: white;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-right: 10px;
  font-size: 1em;
}
.chart-title {
  font-weight: 600;
  font-size: 1.1em;
  color: #2c3e50;
}
.chart-features {
  font-size: 1em;
  color: #7f8c8d;
  margin: 8px 0;
  padding-left: 10px;
  border-left: 3px solid #3498db;
}
.chart-scenario {
  background: #f8f9fa;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.95em;
  color: #34495e;
  margin-top: 10px;
}
</style>

<div class="chart-container">

<div class="chart-card">
  <div class="chart-header">
    <div class="chart-number">1</div>
    <div class="chart-title">📈 折线图 - 时间趋势分析</div>
  </div>
  <div class="chart-features">
    • X轴: 时间 (日/周/月)<br>
    • Y轴: 工作量 (分/项)<br>
    • 多线对比: 支持多人对比
  </div>
  <div class="chart-scenario">应用查看工作量随时间变化趋势</div>
</div>

<div class="chart-card">
  <div class="chart-header">
    <div class="chart-number">2</div>
    <div class="chart-title">📊 柱状图 - 对比分析</div>
  </div>
  <div class="chart-features">
    • 垂直柱状: 人员对比<br>
    • 水平柱状: 工作类型对比<br>
    • 堆叠柱状: 构成分析
  </div>
  <div class="chart-scenario">对比不同人员或工作类型的数据</div>
</div>

<div class="chart-card">
  <div class="chart-header">
    <div class="chart-number">3</div>
    <div class="chart-title">🥧 饼图 - 占比分析</div>
  </div>
  <div class="chart-features">
    • 工作类型占比<br>
    • 分值区间占比<br>
    • 人员贡献占比
  </div>
  <div class="chart-scenario">显示各类别在整体中的占比关系</div>
</div>

<div class="chart-card">
  <div class="chart-header">
    <div class="chart-number">4</div>
    <div class="chart-title">🌞 旭日图 - 层次分析</div>
  </div>
  <div class="chart-features">
    • 多层数据展示<br>
    • 交互式钻取<br>
    • 大小表示重要性
  </div>
  <div class="chart-scenario">展示具有层级结构的复杂数据</div>
</div>

<div class="chart-card">
  <div class="chart-header">
    <div class="chart-number">5</div>
    <div class="chart-title">🌳 矩阵树图 - 矩形树图</div>
  </div>
  <div class="chart-features">
    • 面积表示数值<br>
    • 颜色表示类别<br>
    • 空间利用率高
  </div>
  <div class="chart-scenario">高效利用空间展示层次化数据</div>
</div>

<div class="chart-card">
  <div class="chart-header">
    <div class="chart-number">6</div>
    <div class="chart-title">📅 日历热度图 - 时间密度</div>
  </div>
  <div class="chart-features">
    • 颜色深浅表示工作量<br>
    • 月度视图<br>
    • 节假日标记
  </div>
  <div class="chart-scenario">按日查看工作量分布和密度</div>
</div>

<div class="chart-card">
  <div class="chart-header">
    <div class="chart-number">7</div>
    <div class="chart-title">📐 中位数图 - 分布分析</div>
  </div>
  <div class="chart-features">
    • 显示数据分布<br>
    • 异常值识别<br>
    • 箱线图展示
  </div>
  <div class="chart-scenario">分析数据分布情况和识别异常值</div>
</div>

<div class="chart-card">
  <div class="chart-header">
    <div class="chart-number">8</div>
    <div class="chart-title">🕳️ 漏斗图 - 转化分析</div>
  </div>
  <div class="chart-features">
    • 工作流程转化<br>
    • 效率损失识别<br>
    • 瓶颈分析
  </div>
  <div class="chart-scenario">分析工作流程效率和识别瓶颈</div>
</div>

<div class="chart-card">
  <div class="chart-header">
    <div class="chart-number">9</div>
    <div class="chart-title">📈 双轴组合图 - 综合分析</div>
  </div>
  <div class="chart-features">
    • 折线+柱状组合<br>
    • 双Y轴展示<br>
    • 多维度对比
  </div>
  <div class="chart-scenario">综合展示多种类型的数据关系</div>
</div>

</div>

### 🔍 高级查询 条件查询构建器

#### 条件树SQL语句生成

- 可查询表:
  - 工作量内容固定列表
  - 员工工作量表
  - 城市代码表 (天气功能)

```sql
-- 示例查询条件
...
FROM 员工工作量表
WHERE 日期 BETWEEN '2025-08-01' AND '2025-08-31'
  AND 姓名 = '张三'
  AND 任务内容 LIKE '%巡检%'
  AND 单项分值 >= 10
  AND 核定 is true
```

##### 高级查询示例截图

![高级查询示例截图](https://i.postimg.cc/qv5vybLS/user-def-query.png)

<a id="值班数据统计及导出"></a>

### 值班数据统计及导出

值班统计和输油补贴用于统计和管理员工的值班情况以及相关的输油作业补贴并生成相应的统计报表。

- 该功能主要用于：

  - 记录员工的值班日期
  - 区分普通输油值班和晚10点后输油值班
  - 统计每位员工的值班次数
  - 生成值班统计报表用于补贴发放依据

- 值班数据表

该表详细记录每个员工在指定时间范围内的值班情况：

- **日期**：员工值班的具体日期
- **姓名**：值班员工的姓名
- **晚10点后输油**：标识该次值班是否涉及晚10点后的输油作业（是/否）

- 值班分类统计表

该表按员工分类统计值班情况：

- **姓名**：员工姓名
- **普通输油**：普通输油值班次数（未在晚10点后输油）
- **晚10点后输油**：晚10点后有输油作业的值班次数
- **值班总计**：该员工在统计时间范围内的总值班次数

报表末尾包含合计行，显示所有员工的值班统计总和。

- **数据校验机制**

系统会自动校验统计数据的合理性：

1. 检查普通输油、晚10点后输油和值班总计是否为偶数
2. 检查总值班次数是否超过理论最大值（天数×2）
3. 如果发现数据异常，系统会提示"值班人数与值班合计数据不匹配，请检查!"

<a id="公告发布和修改"></a>

### 公告发布和修改

- 公告发布
  - 添加公告 : 针对本站所有成员发布公告, 可以设置有效期

      **用户登录后如果有新公告，则会在公告页显示并更改该页图标以示提醒**
- 公告修改
  - 修改或删除公告 : 仅管理员可修改

<a id="人脸识别系统"></a>

### 人脸识别系统

#### 🔐 技术架构 人脸识别流程

```mermaid
graph TD
    A[📷 摄像头捕获] --> B[🔍 人脸检测]
    B --> C[📍 特征点定位]
    C --> D[🔢 特征向量提取]
    D --> E[💾 数据库比对]
    E --> F[📊 相似度计算]
    F --> G[⚖️ 阈值判断]
    G -->|✅ 通过\n相似度 ≥ 阈值| H[✅ 登录成功]
    G -->|❌ 失败\n相似度 < 阈值| I[🔑 密码登录]
```

#### 性能指标

- 识别准确率 : ≥99.5% (正常光线)
- 识别速度 : ≤1秒
- 支持角度 : ±30度
- 支持距离 : 0.5-2米
- 光线要求 : 100-10000 lux

### 📸 人脸录入指南

#### 录入流程

```mermaid
graph TD
    A[👤 进入设置] --> B[🔐 权限检查]
    B --> C[📍 位置调整]
    C --> D[📸 多角度采集]
    D --> E[🔍 质量检查]
    E --> F[🔢 特征提取]
    F --> G[💾 保存至数据库]

    A --> A1[设置 → 录入人脸数据]
    B --> B1[确保摄像头权限已开启]
    C --> C1[面部居中，占画面1/3]
    D --> D1[系统自动采集5个角度]
    E --> E1[自动检测照片质量]
    F --> F1[生成128维特征向量]
    G --> G1[显示录入成功提示]
```

#### 录入要求

<div style="overflow-x: auto;">

| 要求项目 | 具体标准 | 不合格示例 |
|:--------:|:--------:|:----------:|
| **光线** | <span style="color: #2E8B57;">均匀自然光</span> | <span style="color: #DC143C;">逆光、强光阴影</span> |
| **角度** | <span style="color: #2E8B57;">正面朝向</span> | <span style="color: #DC143C;">侧脸、低头、仰头</span> |
| **表情** | <span style="color: #2E8B57;">自然中性</span> | <span style="color: #DC143C;">夸张表情、闭眼</span> |
| **遮挡** | <span style="color: #2E8B57;">无遮挡</span> | <span style="color: #DC143C;">眼镜反光、口罩、帽子</span> |
| **清晰度** | <span style="color: #2E8B57;">面部清晰</span> | <span style="color: #DC143C;">模糊、运动模糊</span> |

</div>

### ⚙️ 参数调优

#### 识别阈值设置

- 高安全模式 : 0.8 (严格，误识率低)
- 标准模式 : 0.6 (平衡，推荐)
- 高便利模式 : 0.4 (宽松，速度快)

#### 环境适配

- 室内环境 : 标准模式
- 光线变化 : 开启自适应
- 多人场景 : 开启活体检测

<a id="天气功能"></a>

### 天气功能

### 🌤️ 实时天气 显示内容

- 当前温度 : 实时温度，体感温度
- 天气状况 : 晴、雨、雪、雾等
- 湿度 : 相对湿度百分比
- 风力 : 风向风速等级
- 降水预测 : 短期内降水概率
- 空气质量 : AQI指数和等级

#### 预警信息

- 天气预警 : 暴雨、大风、高温预警
- 限行提醒 : 机动车尾号限行
- 特殊提示 : 恶劣天气注意事项

### 📅 历史天气查询

- 获取指定日期范围内的日天气数据
- 获取指定日期的逐小时天气数据
- 高温天气统计

#### 查询功能

- 日期范围 : 支持365天内查询
- 地点选择 : 支持全国3000+城市
- 数据维度 : 温度、湿度、天气、风力
- 图表展示 : 温度、风力及湿度变化曲线图

#### 应用场景

- 工作量关联 : 分析天气对工作效率影响
- 计划制定 : 根据历史天气制定工作计划
- 异常分析 : 识别天气导致的异常数据

<a id="数据导出"></a>

## 数据导出

### 📊 Excel导出

#### 导出类型

1. 明细数据
   - 包含所有字段
   - 原始数据无加工
   - 支持筛选条件
2. 统计报表
   - 按日/周/月汇总
   - 包含计算字段
   - 图表数据对应
3. 考核报表
   - 绩效考核专用
   - 排名对比数据
   - 领导签字区域

#### 格式规范

- 文件命名 : 站点_全站工作量统计_统计日期区间_时间戳.xlsx
- 工作表 :
  - Sheet1: 统计表
  - Sheet2: 简报
- 格式设置 :
  - 字体: 微软雅黑 12号
  - 边框: 细线边框
  - 颜色: 隔行变色
  - 冻结: 首两行冻结

### 📝 Word导出

#### 报告模板

1. 日报模板

   ```bash
   # 工作量日报
   站点：北京站
   日期：2025年8月11日
   统计人：张三

   ## 今日概况
   - 总工作量：85分
   - 工作项数：12项
   - 参与人员：8人

   ## 详细数据
   [表格数据]

   ## 图表分析
   [图表]

   ## 备注说明
   [特殊情况说明]
   ```

2. 月报模板
   - 月度工作总结
   - 人员排名情况
   - 环比分析
   - 文件命名 : 站点_用户姓名_统计日期区间_时间戳.docx

#### 自定义模板 (Todo)

- 模板管理 : 管理员可创建模板
- 变量替换 : 支持动态数据替换
- 样式统一 : 企业标准格式
- 批量生成 : 一键生成多份报告

### 🛠 个人设置

普通用户可以在个人设置中配置自己的使用偏好，这些设置仅对当前用户生效。

<style>
.settings-category {
  background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
  color: white;
  padding: 10px 15px;
  border-radius: 8px 8px 0 0;
  font-weight: bold;
  margin: 20px 0 0 0;
  display: flex;
  align-items: center;
}
.settings-category i {
  margin-right: 10px;
  font-size: 1.2em;
}
.settings-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  border-radius: 0 0 8px 8px;
  overflow: hidden;
  table-layout: fixed;
}
.settings-table th {
  background-color: #f8f9fa;
  padding: 12px 15px;
  text-align: left;
  border-bottom: 2px solid #e9ecef;
}
.settings-table td {
  padding: 12px 15px;
  border-bottom: 1px solid #e9ecef;
  vertical-align: top;
}
.settings-table tr:nth-child(even) {
  background-color: #f8f9fa;
}
.settings-table tr:hover {
  background-color: #e9f7fe;
}
.settings-table th:nth-child(1),
.settings-table td:nth-child(1) {
  width: 25%;
  font-weight: 500;
  color: #495057;
}
.settings-table th:nth-child(2),
.settings-table td:nth-child(2) {
  width: 55%;
  color: #6c757d;
}
.settings-table th:nth-child(3),
.settings-table td:nth-child(3) {
  width: 20%;
  font-weight: 500;
  color: #28a745;
}
</style>

<div class="settings-category">
  <i>🖥️</i>
  <div>界面显示设置</div>
</div>

<table class="settings-table">
  <thead>
    <tr>
      <th>设置项</th>
      <th>功能说明</th>
      <th>默认值</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>主页展示方式</td>
      <td>选择主页显示静态文字或动态特效文字</td>
      <td>静态文字</td>
    </tr>
    <tr>
      <td>天气展示</td>
      <td>是否在主页显示天气信息</td>
      <td>显示</td>
    </tr>
    <tr>
      <td>天气展示方式</td>
      <td>选择天气信息的展示形式（卡片或文字）</td>
      <td>卡片</td>
    </tr>
    <tr>
      <td>天气API选择</td>
      <td>选择使用和风天气或高德天气API</td>
      <td>和风天气</td>
    </tr>
    <tr>
      <td>天气图标</td>
      <td>选择使用系统图标或和风天气图标</td>
      <td>系统图标</td>
    </tr>
    <tr>
      <td>空气质量展示</td>
      <td>是否显示空气质量信息</td>
      <td>不显示</td>
    </tr>
    <tr>
      <td>天气预警展示</td>
      <td>是否显示天气预警信息</td>
      <td>显示</td>
    </tr>
    <tr>
      <td>车辆限行预警</td>
      <td>是否显示车辆限行信息</td>
      <td>显示</td>
    </tr>
  </tbody>
</table>

<div class="settings-category">
  <i>📊</i>
  <div>工作录入设置</div>
</div>

<table class="settings-table">
  <thead>
    <tr>
      <th>设置项</th>
      <th>功能说明</th>
      <th>默认值</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>自动选择日常工作</td>
      <td>是否自动勾选常用工作项</td>
      <td>自动勾选</td>
    </tr>
    <tr>
      <td>工作组排序方式</td>
      <td>选择工作组别按个性化排序或固定排序</td>
      <td>个性化排序</td>
    </tr>
    <tr>
      <td>岗位工作类型</td>
      <td>选择岗位工作类型（值班或白班）</td>
      <td>值班</td>
    </tr>
  </tbody>
</table>

<div class="settings-category">
  <i>🔐</i>
  <div>登录设置</div>
</div>

<table class="settings-table">
  <thead>
    <tr>
      <th>设置项</th>
      <th>功能说明</th>
      <th>默认值</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>用户名密码登录</td>
      <td>是否启用用户名密码登录方式</td>
      <td>启用</td>
    </tr>
    <tr>
      <td>人脸识别登录</td>
      <td>是否启用人脸识别登录方式</td>
      <td>启用</td>
    </tr>
  </tbody>
</table>

#### 个人设置截图

![个人设置截图](https://i.postimg.cc/QMKxbQYt/users-setup.png)

#### 设置操作说明

1. 进入设置：在系统主界面左侧导航菜单中点击"设置"，然后选择"个人设置"
2. 修改配置：在个人设置页面中，通过切换开关来启用或禁用相应的功能
3. 保存设置：系统会自动保存您的设置，刷新页面后生效
4. 恢复默认：如需恢复默认设置，请联系管理员进行重置

#### 注意事项

- 个人设置中的选项仅对当前登录用户生效，不会影响其他用户
- 部分设置项可能需要刷新页面或重新登录才能完全生效
- **如果某些设置项不可见或不可修改，可能是管理员进行了相关限制**

<a id="系统管理"></a>

## 系统管理

### 🔧 管理员功能

<a id="数据库操作"></a>

#### 数据库操作

以下数据库操作功能仅对具有数据库管理员权限(DBA)的用户开放。所有数据库操作都具有潜在风险，请在执行前确保已备份重要数据。

##### 重置PA-Number

重置所有工作量记录的PA-Number编号，使其从1开始重新编号, 步长2。

操作步骤：

```bash
1. 在左侧导航菜单中点击"数据库操作"
2. 选择"重置PA-Number"选项
3. 点击"确认重置"按钮
4. 系统将显示操作结果

注意事项：
- 此操作会重新排列所有工作量记录的编号
- 不会影响工作量数据内容
- 仅建议在编号出现严重混乱时使用
```

##### 重置工作组别热度

重置用户工作组别使用频率统计数据，重新计算各工作组别的使用热度。

操作步骤：

```bash
1. 在左侧导航菜单中点击"数据库操作"
2. 选择"重置工作组别"选项
3. 点击"确认重置工作组别热度"按钮
4. 系统将显示操作结果

注意事项：
- 此操作会清空现有的工作组别使用频率统计
- 系统会重新根据用户实际使用情况计算热度
- 不会影响用户的工作量数据
```

##### 更新ID初始值

更新数据库各表的自增ID初始值，使其与当前最大ID保持一致。

操作步骤：

```bash
1. 在左侧导航菜单中点击"数据库操作"
2. 选择"更新ID初始值"选项
3. 点击"确认更新ID初始值"按钮
4. 系统将显示操作结果

注意事项：
- 此操作会遍历所有数据表并更新自增ID初始值
- 防止ID重复或浪费
- 是数据库维护的重要操作
```

##### 更新PA-Share

更新共享分值（PA-Share）数据，重新计算和同步共享工作量的分值分配。

操作步骤：

```bash
1. 在左侧导航菜单中点击"数据库操作"
2. 选择"更新PA-Share"选项
3. 点击"确认更新PA-Share"按钮
4. 系统将显示操作结果

注意事项：
- 此操作会重新计算所有共享工作量的分值分配
- 可能需要较长时间完成
- 建议在系统使用较少时执行
```

##### 更新固定分值

更新固定分值工作内容的分值，同步到用户工作量记录中。

操作步骤：

```bash
1. 在左侧导航菜单中点击"数据库操作"
2. 选择"更新固定分值"选项
3. 点击"更新固定分值"按钮
4. 再次点击"确认更新"按钮
5. 系统将显示操作结果

注意事项：
- 此操作会根据工作内容的基准分值更新用户记录
- 适用于基准分值调整后的批量更新
- 不会影响用户自定义的分值和共享分值
```

##### 组别名称修改

修改工作组别的名称，同时更新相关引用。

操作步骤：

```bash
1. 在左侧导航菜单中点击"数据库操作"
2. 选择"组别名称修改"选项
3. 在界面中选择要修改的工作组别
4. 输入新的工作组别名称
5. 点击"确认修改"按钮
6. 系统将显示操作结果

注意事项：
- 修改后会同步更新所有相关引用
- 请确保新名称不与其他工作组别重复
- 建议在修改前确认所有用户都不在使用该组别录入数据
```

##### 分组内容调整

调整工作组别中的工作内容，修改工作内容与工作组别的关联关系。

操作步骤：

```bash
1. 在左侧导航菜单中点击"数据库操作"
2. 选择"分组内容调整"选项
3. 选择要调整的工作组别
4. 在工作内容列表中勾选或取消勾选相应内容
5. 点击"保存修改"按钮
6. 系统将显示操作结果

注意事项：
- 调整后会影响新录入工作量的分组显示
- 不会影响已有工作量记录
- 建议调整前导出相关数据作为备份
```

##### 工作内容修改

修改系统中的工作内容条目，包括工作内容描述和基准分值。

操作步骤：

```bash
1. 在左侧导航菜单中点击"数据库操作"
2. 选择"工作内容修改"选项
3. 在搜索框中输入要修改的工作内容或选择工作组别筛选
4. 点击要修改的工作内容条目
5. 点击"保存修改"按钮
6. 系统将显示操作结果

注意事项：
- 修改工作内容描述会影响所有相关记录的显示
- 建议在修改前导出相关数据作为备份
```

##### 数据库备份

执行数据库的完整备份操作，生成SQL格式的备份文件。

操作步骤：

```bash
1. 在左侧导航菜单中点击"数据库操作"
2. 选择"数据库备份"选项
3. 点击"开始备份"按钮
4. 系统将执行备份操作并显示结果
5. 备份文件将保存在MySQL_Backup目录中，文件名包含时间戳

注意事项：
- 备份文件包含数据库的完整数据和结构
- 备份过程可能需要一些时间，取决于数据量大小
- 建议定期执行备份操作
- 备份文件可用于数据恢复或迁移
```

#### 数据库操作安全提示

1. 所有数据库操作都具有潜在风险，请在操作前确认操作目的和影响范围
2. 重要操作前请先执行数据库备份
3. 建议在系统使用较少的时间段执行数据库维护操作
4. 如不确定操作影响，请联系技术支持
5. 操作完成后检查系统功能是否正常

#### 用户权限管理

权限层级:

<style>
.permission-tree {
  display: flex;
  flex-direction: column;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  max-width: 600px;
  margin: 20px 0;
}

.permission-level {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  margin: 8px 0;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
  background: white;
}

.permission-level:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(0,0,0,0.15);
}

.permission-level.main {
  background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
  color: white;
  font-weight: bold;
  font-size: 1.1em;
  border-left: 4px solid #ffd700;
}

.permission-level.secondary {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  color: white;
  border-left: 4px solid #0066cc;
}

.permission-level.tertiary {
  background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
  color: #333;
  border-left: 4px solid #ff6600;
}

.permission-level.fourth {
  background: linear-gradient(135deg, #23ee52ff 0%, #ffd200 100%);
  color: #333;
  border-left: 4px solid #ff6600;
}

.permission-icon {
  margin-right: 12px;
  font-size: 1.2em;
}

.permission-content {
  flex: 1;
}

.permission-items {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 10px;
  margin-top: 10px;
  padding-left: 30px;
}

.permission-item {
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  text-align: center;
  font-size: 1em;
}

.permission-level.main .permission-item {
  background: rgba(255, 255, 255, 0.3);
}

.permission-level.secondary .permission-item {
  background: rgba(255, 255, 255, 0.2);
}

.permission-level.tertiary .permission-item {
  background: rgba(255, 255, 255, 0.3);
}
</style>

<div class="permission-tree">
  <div class="permission-level main">
    <div class="permission-icon">👑</div>
    <div class="permission-content">
      <div>超级管理员 (系统级Root&DBA)</div>
      <div class="permission-items">
        <div class="permission-item">创建站点</div>
        <div class="permission-item">管理所有用户</div>
        <div class="permission-item">系统配置</div>
      </div>
    </div>
  </div>

  <div class="permission-level secondary">
    <div class="permission-icon">🏢</div>
    <div class="permission-content">
      <div>站点管理员 (站点级Admin)</div>
      <div class="permission-items">
        <div class="permission-item">本站用户管理</div>
        <div class="permission-item">本站数据管理</div>
        <div class="permission-item">本站配置</div>
      </div>
    </div>
  </div>

  <div class="permission-level tertiary">
    <div class="permission-icon">👤</div>
    <div class="permission-content">
      <div>普通用户 (个人级User)</div>
      <div class="permission-items">
        <div class="permission-item">个人数据录入</div>
        <div class="permission-item">个人数据查询</div>
        <div class="permission-item">个人设置</div>
      </div>
    </div>
  </div>
  <div class="permission-level fourth">
    <div class="permission-icon">🔎</div>
    <div class="permission-content">
      <div>访客用户 (数据只读Visitor)</div>
      <div class="permission-items">
        <div class="permission-item">所有功能展示</div>
        <div class="permission-item">数据只读</div>
      </div>
    </div>
  </div>
</div>

#### ⚙️ 系统配置参数

<div style="overflow-x: auto;">

| 配置类别 | 配置项 | 默认值 | 可调范围 |
|----------|--------|--------|----------|
| **最大扣分项** | 最大扣分分值 | `-300` | -600 至 -30 |
| **字体大小** | 报表字体大小 | `14` | 10-20 |
| **月天数** | 月最小天数 | `28天` | 27-31天 |
| **共享任务分值** | PA-Share分值最大查询天数 | `60天` | 14-60天 |
| **人脸识别** | 相似度阈值 | `70%` | 50%-90% |
| **人脸识别** | 最大尝试次数 **(Todo)** | `3次` | 1-5次 |
| **工作基数** | 智能推荐工作阈值 | `5次` | 3-20次 |
| **额外输油** | 晚10点后是否输油 | `True` | True/False(1/0) |
| **系统设置** | 会话超时 **(Todo)** | `30分钟` | 10-120分钟 |
| **数据备份** | 自动备份时间 **(Todo)** | `02:00` | 00:00-23:59 |
| **数据备份** | 备份保留天数 **(Todo)** | `5天` | 7-14天 |

</div>

> 💡 **说明**: 带有 **(Todo)** 标记的配置项为待实现功能，当前版本暂未生效。

##### 系统设置截图

![系统设置截图](https://i.postimg.cc/Px2KK4SC/system-setup.png)

#### 数据维护

- 数据清理 : 清理过期日志和临时文件
- 索引优化 : 重建数据库索引提升性能
- 数据校验 : 检查数据完整性和一致性
- 备份验证 : 定期验证备份文件可用性

### 📋 审计日志 (Todo)

#### 日志类型

- 登录日志 : 用户登录时间、IP、方式
- 操作日志 : 关键操作记录
- 数据日志 : 数据修改前后对比
- 系统日志 : 系统异常和错误

#### 日志查询

查询条件:

- 用户: 指定用户或全部
- 时间: 日期范围选择
- 类型: 登录/操作/数据/系统
- 关键词: 操作内容搜索

<a id="故障排除"></a>

## 故障排除

### 🔍 常见问题解决方案

<style>
.faq-category {
  background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
  color: white;
  padding: 10px 15px;
  border-radius: 8px 8px 0 0;
  font-weight: bold;
  margin: 20px 0 0 0;
  display: flex;
  align-items: center;
}
.faq-category i {
  margin-right: 10px;
  font-size: 1.2em;
}
.faq-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  border-radius: 0 0 8px 8px;
  overflow: hidden;
}
.faq-table th {
  background-color: #f8f9fa;
  padding: 12px 15px;
  text-align: left;
  border-bottom: 2px solid #e9ecef;
}
.faq-table td {
  padding: 12px 15px;
  border-bottom: 1px solid #e9ecef;
}
.faq-table tr:nth-child(even) {
  background-color: #f8f9fa;
}
.faq-table tr:hover {
  background-color: #e9f7fe;
}
.faq-table th:nth-child(1),
.faq-table td:nth-child(1) {
  width: 25%;
  font-weight: 500;
  color: #495057;
}
.faq-table th:nth-child(2),
.faq-table td:nth-child(2) {
  width: 35%;
  color: #6c757d;
}
.faq-table th:nth-child(3),
.faq-table td:nth-child(3) {
  width: 40%;
  font-weight: 500;
  color: #28a745;
}
.problem {
  color: #dc3545;
  font-weight: 500;
}
.cause {
  color: #ff7300ff;
}
.solution {
  color: #28a745;
  font-weight: 500;
}
</style>

<div class="faq-category">
  <i>🔐</i>
  <div>登录问题</div>
</div>

<table class="faq-table">
  <thead>
    <tr>
      <th>问题现象</th>
      <th>可能原因</th>
      <th>解决方案</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><span class="problem">页面无法打开</span></td>
      <td><span class="cause">服务未启动</span></td>
      <td><span class="solution">streamlit run gru-pa.py</span></td>
    </tr>
    <tr>
      <td><span class="problem">密码错误</span></td>
      <td><span class="cause">忘记密码</span></td>
      <td><span class="solution">联系管理员重置</span></td>
    </tr>
    <tr>
      <td><span class="problem">人脸识别失败</span></td>
      <td><span class="cause">光线不足</span></td>
      <td><span class="solution">改善光线条件</span></td>
    </tr>
    <tr>
      <td><span class="problem">摄像头无权限</span></td>
      <td><span class="cause">浏览器设置</span></td>
      <td><span class="solution">允许摄像头访问</span></td>
    </tr>
  </tbody>
</table>

<div class="faq-category">
  <i>📊</i>
  <div>数据问题</div>
</div>

<table class="faq-table">
  <thead>
    <tr>
      <th>问题现象</th>
      <th>可能原因</th>
      <th>解决方案</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><span class="problem">数据不显示</span></td>
      <td><span class="cause">未审核</span></td>
      <td><span class="solution">管理员审核数据</span></td>
    </tr>
    <tr>
      <td><span class="problem">统计不准确</span></td>
      <td><span class="cause">时间范围错误</span></td>
      <td><span class="solution">重新选择时间范围</span></td>
    </tr>
    <tr>
      <td><span class="problem">无法导出</span></td>
      <td><span class="cause">浏览器拦截</span></td>
      <td><span class="solution">允许弹窗和下载</span></td>
    </tr>
    <tr>
      <td><span class="problem">图表空白</span></td>
      <td><span class="cause">无数据</span></td>
      <td><span class="solution">检查查询条件</span></td>
    </tr>
  </tbody>
</table>

<div class="faq-category">
  <i>⚡</i>
  <div>性能问题</div>
</div>

<table class="faq-table">
  <thead>
    <tr>
      <th>问题现象</th>
      <th>可能原因</th>
      <th>解决方案</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><span class="problem">加载缓慢</span></td>
      <td><span class="cause">数据量大</span></td>
      <td><span class="solution">缩小查询时间范围</span></td>
    </tr>
    <tr>
      <td><span class="problem">系统卡顿</span></td>
      <td><span class="cause">内存不足</span></td>
      <td><span class="solution">重启服务或升级硬件</span></td>
    </tr>
    <tr>
      <td><span class="problem">数据库慢</span></td>
      <td><span class="cause">索引缺失</span></td>
      <td><span class="solution">管理员重建索引</span></td>
    </tr>
    <tr>
      <td><span class="problem">导出超时</span></td>
      <td><span class="cause">数据量过大</span></td>
      <td><span class="solution">分批导出</span></td>
    </tr>
  </tbody>
</table>

### 🚨 紧急处理

#### 系统完全无法访问

1. 检查服务状态

   ```bash
   # Linux
   ps aux | grep streamlit

   # Windows
   tasklist | findstr python
   ```

2. 重启服务

   ```bash
   # 停止服务
   pkill -f streamlit

   # 重新启动
   nohup streamlit run gru-pa.py
   ```

3. 检查端口占用

   ```bash
   netstat -tulnp | grep 8510
   ```

#### 数据库连接失败

1. 检查MySQL服务

   ```bash
   # Linux
   systemctl status mysql

   # Windows
   net start mysql
   ```

2. 测试连接

   ```bash
   mysql -u gru_pa_user -p -h localhost gru_pa
   ```

3. 修复权限

   ```sql
   GRANT ALL PRIVILEGES ON gru_pa.* TO 'gru_pa_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

<a id="安全指南"></a>

## 安全指南

### 🔒 安全最佳实践

#### 密码安全

- 复杂度要求 : 大小写字母+数字+特殊字符
- 长度要求 : 最少8位，推荐12位以上
- 更换周期 : 90天强制更换
- 历史密码 : 不能重复使用最近5次密码
- 登录失败 : 连续5次失败锁定30分钟

#### 数据安全

- 传输加密 : 使用HTTPS协议
- 存储加密 : 敏感数据AES加密
- 备份加密 : 备份文件加密存储
- 访问控制 : 基于IP的白名单
- 审计跟踪 : 所有操作可追踪

#### 系统安全

- 最小权限 : 用户仅拥有必要权限
- 定期更新 : 及时更新系统和依赖
- 防火墙 : 仅开放必要端口
- 监控告警 : 异常行为实时告警
- 应急响应 : 安全事件处理预案

### 📚 文档资源

- 操作手册 : operation_manual.md (本文件)
- 更新日志 : CHANGELOG.md
- 项目说明 : README.md
- 许可证 : LICENSE

### 🐞 问题反馈

提交Issue时请包含：

1. 系统信息 : OS版本、Python版本、浏览器版本
2. 错误信息 : 完整错误信息
3. 复现步骤 : 详细操作步骤 (推荐)
4. 截图 : 错误界面截图 (推荐)
5. 数据样本 : 如有必要提供数据样本

### 📈 版本更新

- 更新通知 : 系统内消息推送
- 自动更新 : 使用Git管理代码

  ```bash
  git pull origin main
  pip install -r requirements.txt --upgrade
  ```

- 版本兼容 : 向下兼容，平滑升级

## 附录

### 📄 文件清单

<style>
.file-list {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin: 20px 0;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}
.file-item {
  margin: 8px 0;
  padding: 8px 12px;
  border-radius: 6px;
  transition: all 0.2s ease;
}
.file-item:hover {
  background: #e9f7fe;
  transform: translateX(5px);
}
.file-name {
  font-family: 'Courier New', monospace;
  font-weight: 600;
  color: #2c3e50;
}
.file-comment {
  color: #6c757d;
  font-size: 1em;
  margin-left: 10px;
}
.folder {
  color: #2980b9;
  font-weight: bold;
}
.sub-folder {
  color: #3498db;
  font-weight: 500;
}
.file-category {
  background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 1em;
  margin: 15px 0 10px 0;
  display: inline-block;
}
</style>

<div class="file-list">

<div class="file-category">⚙️ 配置文件</div>
<div class="file-item"><span class="file-name">.streamlit/config.toml</span> <span class="file-comment"># Streamlit配置文件</span></div>
<div class="file-item"><span class="file-name">.mysql.cnf</span> <span class="file-comment"># MySQL配置文件</span></div>

<div class="file-category">🐍 主程序文件</div>
<div class="file-item"><span class="file-name">gru-pa.py</span> <span class="file-comment"># 入口文件及主程序 All in one</span></div>
<div class="file-item"><span class="file-name">mysql_pool_cpython.pyc</span> <span class="file-comment"># MySQL连接池模块(不同步)</span></div>

<div class="file-category">🧩 功能模块</div>
<div class="file-item"><span class="file-name">commFunc.py</span> <span class="file-comment"># 公共函数模块</span></div>
<div class="file-item"><span class="file-name">gen_badges.py</span> <span class="file-comment"># 徽章生成模块</span></div>
<div class="file-item"><span class="file-name">face_login.py</span> <span class="file-comment"># 人脸登录模块</span></div>
<div class="file-item"><span class="file-name">hf_weather.py</span> <span class="file-comment"># 和风天气API模块</span></div>
<div class="file-item"><span class="file-name">gd_weather.py</span> <span class="file-comment"># 高德天气API模块</span></div>
<div class="file-item"><span class="file-name">gen_license_plate.py</span> <span class="file-comment"># 车牌生成模块</span></div>

<div class="file-category">📦 第三方库</div>
<div class="file-item"><span class="file-name">dlib</span> <span class="file-comment"># dlib人脸识别库whl文件、编译说明及68个点模型文件</span></div>

<div class="file-category">📚 文档资源</div>
<div class="file-item"><span class="file-name">documents</span> <span class="file-comment"># 文档文件(不同步)</span></div>
<div class="file-item"><span class="file-name">operation_manual.md</span> <span class="file-comment"># 操作手册文件</span></div>
<div class="file-item"><span class="file-name">README.md</span> <span class="file-comment"># 项目说明文件</span></div>
<div class="file-item"><span class="file-name">CHANGELOG.md</span> <span class="file-comment"># 项目更新日志</span></div>

<div class="file-category">🔤 资源文件</div>
<div class="file-item"><span class="file-name">fonts</span> <span class="file-comment"># 字体文件</span></div>
<div class="file-item"><span class="file-name">ID_Photos</span> <span class="file-comment"># 用户人脸图像, 用于生成识别数据</span></div>

<div class="file-category">🖼️ 图片资源</div>
<div class="file-item"><span class="file-name">Images</span> <span class="file-comment"># 图片文件</span></div>
<div class="file-item"><span class="file-name">&nbsp;&nbsp;∟ badges</span> <span class="file-comment"># 徽章文件</span></div>
<div class="file-item"><span class="file-name">&nbsp;&nbsp;∟ Clock-Images</span> <span class="file-comment"># 时钟图片</span></div>
<div class="file-item"><span class="file-name">&nbsp;&nbsp;∟ license_plate</span> <span class="file-comment"># 车牌图片</span></div>
<div class="file-item"><span class="file-name">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;∟ background</span> <span class="file-comment"># 车牌生成背景图片</span></div>
<div class="file-item"><span class="file-name">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;∟ vehicle_logo</span> <span class="file-comment"># 汽车品牌logo</span></div>
<div class="file-item"><span class="file-name">&nbsp;&nbsp;∟ logos</span> <span class="file-comment"># 依赖库logo文件</span></div>
<div class="file-item"><span class="file-name">&nbsp;&nbsp;∟ snapshot</span> <span class="file-comment"># 截图保存</span></div>

<div class="file-category">🔧 脚本工具</div>
<div class="file-item"><span class="file-name">MyComponentsScript</span> <span class="file-comment"># 自定义组件脚本, txt格式</span></div>
<div class="file-item"><span class="file-name">DBBackup.ps1</span> <span class="file-comment"># 数据库备份PS脚本</span></div>
<div class="file-item"><span class="file-name">restoredb.bat</span> <span class="file-comment"># 数据库恢复bat脚本</span></div>

<div class="file-category">🗄️ 数据文件</div>
<div class="file-item"><span class="file-name">MySQL_Backup</span> <span class="file-comment"># MySQL备份文件</span></div>
<div class="file-item"><span class="file-name">user_pa</span> <span class="file-comment"># 用户统计数据导出文档 (不同步)</span></div>

<div class="file-category">📋 依赖管理</div>
<div class="file-item"><span class="file-name">requirements.txt</span> <span class="file-comment"># 自动安装依赖文件</span></div>

<div class="file-category">🔤 拼写检查</div>
<div class="file-item"><span class="file-name">CSC-Common-CustomDict.txt</span> <span class="file-comment"># CSpell自定义通用字典文件</span></div>
<div class="file-item"><span class="file-name">CSC-Project-CustomDict.txt</span> <span class="file-comment"># CSpell自定义字典文件</span></div>

</div>

### 🎯 快速命令参考

#### 启动系统

```bash
streamlit run gru-pa.py
```

#### 后台启动

```bash
nohup streamlit run gru-pa.py
```

#### 数据库备份 (需配置.mysql.cnf文件)

```bash
./DBBackup.ps1         # Windows
./DBBackup.sh          # Linux
```

#### 数据库恢复

```bash
./restoredb.bat        # Windows
./restoredb.sh         # Linux
```

#### 更新系统

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

### GRU-PA站室绩效考核系统 让管理更简单，让考核更公平

📖 文档 | 🐞 反馈 | ⭐ 点赞

手册版本: v1.1.5 | 更新时间: 2025-08-12 | 作者: Simon Lau

版权说明 : 本手册版权归GRU-PA项目所有，遵循MIT开源协议。欢迎转载、修改和再发布，但请注明出处。

<a id="技术支持"></a>

### 技术支持

联系作者 : <simonpek@163.com>
