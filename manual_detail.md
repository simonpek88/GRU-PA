# GRU-PA 站室绩效考核系统完整操作手册

## 📋 目录

1.系统概述
2.系统安装与配置
3.快速入门
4.用户管理
5.工作量管理
6.数据统计分析
7.人脸识别系统
8.天气功能
9.数据导出
10.系统管理
11.故障排除
12.安全指南
13.技术支持

## 系统概述

### 🎯 系统定位

GRU-PA (Grass-roots unit Performance Appraisal system) 是一款专为基层站室设计的绩效考核管理系统，集成了工作量录入、统计分析、人脸识别、天气查询等现代化管理功能。

### 🏗️ 技术架构

- 前端框架 : Streamlit 1.47.0
- 后端语言 : Python 3.9-3.12
- 数据库 : MySQL 8.4.5 LTS
- 人脸识别 : Dlib 20.0.0 + OpenCV 4.12
- 图表可视化 : Plotly 6.2.0 + Nivo
- 文档处理 : python-docx 1.2.0 + openpyxl 3.1.5

### ✨ 核心特性

- 双因子认证 : 密码 + 人脸识别双重验证
- 智能录入 : 支持批量录入、模板导入、语音输入
- 多维分析 : 9种图表类型，支持时间序列分析
- 实时天气 : 集成和风天气API，支持历史天气查询
- 一键导出 : Excel/Word双格式，支持自定义模板
- 权限管控 : 基于RBAC的精细化权限管理

## 系统安装与配置

### 📋 系统要求

#### 硬件要求

组件 最低配置 推荐配置 CPU Intel i5 4代 Intel i7 10代或AMD Ryzen 5 内存 8GB DDR3 16GB DDR4 存储 50GB HDD 200GB SSD 网络 100Mbps 摄像头 1080p (人脸识别专用)
软件环境
软件 版本要求 下载地址
Python 3.9-3.12.6 [Python官网](https://www.python.org)
MySQL 8.4.5 LTS [MySQL官网](https://dev.mysql.com)
Git 2.30+ [Git官网](https://git-scm.com)
Visual Studio Build Tools 2019+ (Windows编译dlib用)

### 🚀 安装步骤

1. 环境准备

    ```bash
    # Windows系统
    # 安装Python时勾选"Add Python to PATH"
    # 安装MySQL时记住root密码

    # Linux系统 (Ubuntu/Debian)
    sudo apt update && sudo apt 
    upgrade -y
    sudo apt install python3.12 
    python3-pip mysql-server-8.4 git 
    build-essential cmake
    ```

2. 获取源代码

    ```bash
    # 方法1: Git克隆
    git clone https://github.com/
    simonpek88/GRU-PA.git
    cd GRU-PA

    # 方法2: 直接下载
    # 从GitHub Releases下载最新版本ZIP包
    ```

3. 安装依赖

    ```bash
    # 创建虚拟环境 (推荐)
    python -m venv gru-pa-env
    source gru-pa-env/bin/activate  #Linux/Mac
    # 或
    gru-pa-env\Scripts\activate     #Windows

    # 安装Python包
    pip install -r requirements.txt

    # 安装Dlib (Windows)
    pip install dlib/dlib-20.0.
    0-cp312-cp312-win_amd64.whl

    # 安装Dlib (Linux/Mac编译)
    cd dlib
    mkdir build && cd build
    cmake .. -DDLIB_USE_CUDA=1 
    -DUSE_AVX_INSTRUCTIONS=1
    cmake --build .
    cd .. && python setup.py install
    ```

4. 数据库配置

    ```bash
    -- 登录MySQL
    mysql -u root -p

    -- 创建数据库
    CREATE DATABASE gru_pa DEFAULT 
    CHARACTER SET utf8mb4 COLLATE 
    utf8mb4_unicode_ci;

    -- 创建用户并授权
    CREATE USER 
    'gru_pa_user'@'localhost' 
    IDENTIFIED BY 
    'your_secure_password';
    GRANT ALL PRIVILEGES ON gru_pa.* 
    TO 'gru_pa_user'@'localhost';
    FLUSH PRIVILEGES;

    -- 导入初始数据
    mysql -u gru_pa_user -p gru_pa < 
    MySQL_Backup/GRU-PA-MySQL_Backup_*.
    sql
    ```

5. 配置文件设置

    ```bash
    # .streamlit/config.toml
    [server]
    port = 8510
    address = "0.0.0.0"
    enableCORS = false

    [browser]
    gatherUsageStats = false
    ```

### 🏁 启动系统

开发环境

```bash
# 直接启动
streamlit run gru-pa.py

# 指定参数启动
streamlit run gru-pa.py --server.
port 8510 --server.address 0.0.0.0
```

生产环境

```bash
# 使用screen保持后台运行 (Linux)

screen -S gru-pa
streamlit run gru-pa.py --server.
port 8510 --server.address 0.0.0.0
--server.headless true
#  按Ctrl+A+D退出screen

#  使用systemd服务 (Linux)
sudo cp gru-pa.service /etc/
systemd/system/
sudo systemctl enable gru-pa
sudo systemctl start gru-pa

#  Windows后台运行
start /B python -m streamlit run
gru-pa.py --server.port 8510 >
gru-pa.log 2>&1
```

## 快速入门

### 🎯 首次使用流程 1. 管理员初始化

```bash
#  使用默认管理员账号登录
#  用户名: admin  密码: 1234
#  站点: 北京站
```

基础配置

1. 创建站点 : 系统设置 → 站点管理
2. 添加用户 : 用户管理 → 添加用户
3. 设置工作内容 : 基础数据 → 工作内容管理
4. 配置权限 : 权限管理 → 角色权限设置

初次登录流程

1. 访问系统 : <http://localhost:8510>
2. 选择站点 : 选择所属站点
3. 用户登录 : 选择用户名，输入密码
4. 首次登录 : 系统强制修改初始密码
5. 人脸录入 : 设置 → 录入人脸数据

## 用户管理

### 👥 用户角色体系

角色 权限范围 典型用户 超级管理员 全系统管理 IT管理员 站点管理员 站点内管理 站长 部门主管 部门管理 班长 普通员工 个人操作 一般员工 访客 只读权限 临时用户

### 📝 用户操作指南

- 修改密码 : 账户 → 密码修改
- 找回密码 : 联系管理员重置
- 密码策略 : 8-20位，包含大小写+数字+特殊字符
- 定期更新 : 建议90天更换一次密码 个人信息维护
- 基本信息 : 姓名、部门、职位
- 联系方式 : 电话、邮箱、微信
- 工作信息 : 工号、入职时间、岗位
- 个人设置 : 主题偏好、默认设置

## 工作量管理

### 📊 工作量录入系统

#### 批量录入 - 智能模式

操作路径: 功能 → 工作量批量录入

1. **日期选择**
   - 默认: 昨日日期
   - 范围: 支持7天内批量选择
   - 快捷: 今天、昨天、本周、本月

2. **工作内容选择**
   - 搜索框: 支持模糊搜索
   - 分类显示: 按工作类型分组
   - 收藏夹: 常用工作快速选择
   - 历史记录: 最近使用的工作

3. **分值设置**
   - 自动匹配: 根据工作内容自动加载分值
   - 手动调整: 可修改系统建议分值
   - 批量设置: 统一设置相同分值
   - 范围限制: 1-100分，步长0.5

4. **智能推荐**
   - 基于历史: 推荐相似日期的工作
   - 基于岗位: 推荐岗位相关的工作
   - 基于习惯: 学习个人工作习惯

#### 手工录入 - 精准模式

#### 减分项录入

操作路径: 功能 → 工作减分项录入

减分项类型:
- 迟到: -2分/次 (15分钟内)
- 早退: -2分/次 (15分钟内)
- 请假: -10分/天 (事假)
- 缺勤: -20分/天 (无故)
- 工作失误: -5至-50分 (按程度)

录入要求:
- 必须选择减分项类型
- 填写具体原因
- 上传证明材料(可选)
- 管理员审核后生效

### 📈 数据审核流程 审核状态

- 待审核 : 刚提交，等待审核
- 已通过 : 审核通过，计入统计
- 已退回 : 审核不通过，需修改
- 已修改 : 修改后重新提交 审核权限
- 本人 : 只能查看，不能审核
- 班长 : 可审核班组成员
- 站长 : 可审核全站人员
- 管理员 : 可审核所有记录

## 数据统计分析

### 📊 统计维度 时间维度

- 日报 : 每日工作量明细
- 周报 : 本周vs上周对比
- 月报 : 本月趋势分析
- 季报 : 季度工作总结
- 年报 : 年度绩效考核 人员维度
- 个人 : 个人工作轨迹
- 班组 : 班组工作对比
- 站点 : 站点整体情况
- 公司 : 多站点汇总 工作维度
- 工作类型 : 各类工作占比
- 分值分布 : 高分/低分工作识别
- 效率分析 : 单位时间工作量
- 质量评估 : 工作质量评分

### 📈 图表系统 9种图表类型详解

1. 折线图 - 时间趋势分析
   - X轴: 时间(日/周/月)
   - Y轴: 工作量(分/项)
   - 多线对比: 支持多人对比
2. 柱状图 - 对比分析
   - 垂直柱状: 人员对比
   - 水平柱状: 工作类型对比
   - 堆叠柱状: 构成分析
3. 饼图 - 占比分析
   - 工作类型占比
   - 分值区间占比
   - 人员贡献占比
4. 旭日图 - 层次分析
   - 多层数据展示
   - 交互式钻取
   - 大小表示重要性
5. 矩阵树图 - 矩形树图
   - 面积表示数值
   - 颜色表示类别
   - 空间利用率高
6. 日历热度图 - 时间密度
   - 颜色深浅表示工作量
   - 月度视图
   - 节假日标记
7. 中位数图 - 分布分析
   - 显示数据分布
   - 异常值识别
   - 箱线图展示
8. 漏斗图 - 转化分析
   - 工作流程转化
   - 效率损失识别
   - 瓶颈分析
9. 组合图 - 综合分析
   - 折线+柱状组合
   - 双Y轴展示
   - 多维度对比

### 🔍 高级查询 条件查询构建器

-- 示例查询条件
WHERE 工作日期 BETWEEN '2025-08-01'
AND '2025-08-31'
  AND 用户 IN ('张三', '李四')
  AND 工作内容 LIKE '%巡检%'
  AND 分值 >= 10
  AND 审核状态 = '已通过'

## 人脸识别系统

### 🔐 技术架构 人脸识别流程

#### graph TD

    A[摄像头捕获] --> B[人脸检测]
    B --> C[特征点定位]
    C --> D[特征向量提取]
    D --> E[数据库比对]
    E --> F[相似度计算]
    F --> G[阈值判断]
    G -->|通过| H[登录成功]
    G -->|失败| I[密码登录]

#### 性能指标

- 识别准确率 : ≥99.5% (正常光线)
- 识别速度 : ≤1秒
- 支持角度 : ±30度
- 支持距离 : 0.5-2米
- 光线要求 : 100-10000 lux

### 📸 人脸录入指南 录入步骤

1. 进入设置 : 设置 → 录入人脸数据
2. 权限检查 : 确保摄像头权限已开启
3. 位置调整 : 面部居中，占画面1/3
4. 多角度采集 : 系统自动采集5个角度
5. 质量检查 : 自动检测照片质量
6. 特征提取 : 生成128维特征向量
7. 保存完成 : 显示录入成功提示 录入要求

要求项目 具体标准 不合格示例 光线 均匀自然光 逆光、强光阴影 角度 正面朝向 侧脸、低头、仰头 表情 自然中性 夸张表情、闭眼 遮挡 无遮挡 眼镜反光、口罩、帽子 清晰度 面部清晰 模糊、运动模糊

### ⚙️ 参数调优 识别阈值设置

- 高安全模式 : 0.8 (严格，误识率低)
- 标准模式 : 0.6 (平衡，推荐)
- 高便利模式 : 0.4 (宽松，速度快) 环境适配
- 室内环境 : 标准模式
- 室外环境 : 高安全模式
- 光线变化 : 开启自适应
- 多人场景 : 开启活体检测

## 天气功能

### 🌤️ 实时天气 显示内容

- 当前温度 : 实时温度，体感温度
- 天气状况 : 晴、雨、雪、雾等
- 湿度 : 相对湿度百分比
- 风力 : 风向风速等级
- 空气质量 : AQI指数和等级
- 生活指数 : 紫外线、穿衣、运动建议 预警信息
- 天气预警 : 暴雨、大风、高温预警
- 限行提醒 : 机动车尾号限行
- 特殊提示 : 恶劣天气注意事项

### 📅 历史天气查询 查询功能

- 日期范围 : 支持365天内查询
- 地点选择 : 支持全国3000+城市
- 数据维度 : 温度、湿度、天气、风力
- 图表展示 : 温度变化曲线图 应用场景
- 工作量关联 : 分析天气对工作效率影响
- 计划制定 : 根据历史天气制定工作计划
- 异常分析 : 识别天气导致的异常数据

## 数据导出

### 📊 Excel导出 导出类型

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
   - 领导签字区域 格式规范

- 文件命名 : GRU-PA_站点_日期_类型.xlsx
- 工作表 :
  - Sheet1: 数据明细
  - Sheet2: 统计汇总
  - Sheet3: 图表数据
- 格式设置 :
  - 字体: 微软雅黑 11号
  - 边框: 细线边框
  - 颜色: 隔行变色
  - 冻结: 首行冻结

### 📝 Word导出 报告模板

1. 日报模板

   ```bash
   # 工作量日报
   站点：北京站
   日期：2025年8月11日
   统计人：张三

   ## 今日概况
   - 总工作量：85分
   - 工作项数：12项
   - 参与人员：8人

   ## 详细数据
   [表格数据]

   ## 图表分析
   [图表截图]

   ## 备注说明
   [特殊情况说明]
   ```

2. 月报模板
   - 月度工作总结
   - 人员排名情况
   - 同比环比分析
   - 下月工作计划 自定义模板

- 模板管理 : 管理员可创建模板
- 变量替换 : 支持动态数据替换
- 样式统一 : 企业标准格式
- 批量生成 : 一键生成多份报告

## 系统管理

### 🔧 管理员功能 用户权限管理

```bash
权限层级:
├── 超级管理员 (系统级)
│   ├── 创建站点
│   ├── 管理所有用户
│   └── 系统配置
├── 站点管理员 (站点级)
│   ├── 本站用户管理
│   ├── 本站数据管理
│   └── 本站配置
├── 部门主管 (部门级)
│   ├── 部门用户管理
│   ├── 部门数据审核
│   └── 部门报表
└── 普通用户 (个人级)
    ├── 个人数据录入
    ├── 个人数据查询
    └── 个人设置
```

系统配置项
配置类别 配置项 默认值 范围 系统设置 最大查询天数 30天 7-365天 系统设置 密码有效期 90天 30-365天 系统设置 会话超时 30分钟 10-120分钟 人脸识别 相似度阈值 0.6 0.4-0.8 人脸识别 最大尝试次数 3次 1-5次 数据备份 自动备份时间 02:00 00:00-23:59 数据备份 备份保留天数 30天 7-365天
 数据维护

- 数据清理 : 清理过期日志和临时文件
- 索引优化 : 重建数据库索引提升性能
- 数据校验 : 检查数据完整性和一致性
- 备份验证 : 定期验证备份文件可用性

### 📋 审计日志 日志类型

- 登录日志 : 用户登录时间、IP、方式
- 操作日志 : 关键操作记录
- 数据日志 : 数据修改前后对比
- 系统日志 : 系统异常和错误 日志查询

查询条件:
- 用户: 指定用户或全部
- 时间: 日期范围选择
- 类型: 登录/操作/数据/系统
- 关键词: 操作内容搜索

## 故障排除

### 🔍 常见问题解决方案 登录问题

问题现象 可能原因 解决方案 页面无法打开 服务未启动 streamlit run gru-pa.py 密码错误 忘记密码 联系管理员重置 人脸识别失败 光线不足 改善光线条件 摄像头无权限 浏览器设置 允许摄像头访问
数据问题
问题现象 可能原因 解决方案 数据不显示 未审核 管理员审核数据 统计不准确 时间范围错误 重新选择时间范围 无法导出 浏览器拦截 允许弹窗和下载 图表空白 无数据 检查查询条件
性能问题
问题现象 可能原因 解决方案 加载缓慢 数据量大 缩小查询时间范围 系统卡顿 内存不足 重启服务或升级硬件 数据库慢 索引缺失 管理员重建索引 导出超时 数据量过大 分批导出

### 🚨 紧急处理 系统完全无法访问

1. 检查服务状态

   ```bash
   # Linux
   ps aux | grep streamlit

   # Windows
   tasklist | findstr python
   ```

2. 重启服务

   ```bash

   # 停止服务
   pkill -f streamlit

   # 重新启动
   nohup streamlit run gru-pa.py >
   gru-pa.log 2>&1 &
   ```

3. 检查端口占用

   ```bash
   netstat -tulnp | grep 8510
   ```

数据库连接失败

1. 检查MySQL服务

   ```bash
   # Linux
   systemctl status mysql

   # Windows
   net start mysql
   ```

2. 测试连接

   ```bash

   mysql -u gru_pa_user -p -h
   localhost gru_pa
   ```

3. 修复权限

   ```bash

   GRANT ALL PRIVILEGES ON gru_pa.*
   TO 'gru_pa_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

## 安全指南

### 🔒 安全最佳实践 密码安全

- 复杂度要求 : 大小写字母+数字+特殊字符
- 长度要求 : 最少8位，推荐12位以上
- 更换周期 : 90天强制更换
- 历史密码 : 不能重复使用最近5次密码
- 登录失败 : 连续5次失败锁定30分钟 数据安全
- 传输加密 : 使用HTTPS协议
- 存储加密 : 敏感数据AES加密
- 备份加密 : 备份文件加密存储
- 访问控制 : 基于IP的白名单
- 审计跟踪 : 所有操作可追踪 系统安全
- 最小权限 : 用户仅拥有必要权限
- 定期更新 : 及时更新系统和依赖
- 防火墙 : 仅开放必要端口
- 监控告警 : 异常行为实时告警
- 应急响应 : 安全事件处理预案

### 📚 文档资源

- 更新日志 : CHANGELOG.md
- FAQ文档 : FAQ.md

### 🐛 问题反馈

提交Issue时请包含：

1. 系统信息 : OS版本、Python版本、浏览器版本
2. 错误信息 : 完整错误日志
3. 复现步骤 : 详细操作步骤
4. 截图 : 错误界面截图
5. 数据样本 : 如有必要提供数据样本

### 📈 版本更新

- 检查更新 : 系统右上角"检查更新"按钮
- 更新通知 : 系统内消息推送
- 手动更新 :

  ```bash
  git pull origin main
  pip install -r requirements.txt
  --upgrade
  ```

- 版本兼容 : 向下兼容，平滑升级

## 附录

### 📄 文件清单

```bash

GRU-PA/
├── gru-pa.py                # 主程序文件
├── commFunc.py              # 公共函数库
├── face_login.py            # 人脸识别模块
├── hf_weather.py            # 和风天气API
├── gd_weather.py            # 高德天气API
├── gen_badges.py            # 徽章生成器
├── gen_license_plate.py     # 车牌生成器
├── requirements.txt         # 依赖包列表
├── README.md                # 项目说明
├── CHANGELOG.md             # 更新日志
├── operation_manual.md      # 操作手册
├── manual.md                # 本完整手册
├── LICENSE                  # 开源协议
├── .streamlit/config.toml   #Streamlit配置
├── .gitignore               # Git忽略文件
├── DBBackup.ps1             # 数据库备份脚本
├── restoredb.bat            # 数据库恢复脚本
├── dlib/                    # Dlib相关文件
├── documents/               # 文档目录
├── fonts/                   # 字体文件
├── ID_Photos/               # 人脸照片
├── Images/                  # 图片资源
├── MyComponentsScript/      # 自定义组件
├── MySQL_Backup/            # 数据库备份
└── .vscode/                 # VSCode配置
```

### 🎯 快速命令参考

####  启动系统

```bash
streamlit run gru-pa.py
```

####  后台启动

```bash
nohup streamlit run gru-pa.py >gru-pa.log 2>&1 &
```

####  数据库备份

```bash
./DBBackup.ps1         # Windows
./DBBackup.sh          # Linux
```

####  数据库恢复

```bash
./restoredb.bat        # Windows
./restoredb.sh         # Linux
```

####  查看日志

```bash
tail -f gru-pa.log
```

####  更新系统

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

GRU-PA站室绩效考核系统 让管理更简单，让考核更公平

📖 文档 | 🐛 反馈 | ⭐ 点赞

版本: v0.13.1352 | 更新时间: 2025-08-11 | 作者: Simon Lau

版权说明 : 本手册版权归GRU-PA项目所有，遵循MIT开源协议。欢迎转载、修改和再发布，但请注明出处。
