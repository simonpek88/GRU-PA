import os

from pyecharts import options as opts
from pyecharts.charts import Gauge
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions


def create_gauge_chart(name, value, min_value, max_value, start_angle, end_angle, x, y):
    gauge = (
        Gauge()
        .add(
            "",
            [(name, value)],
            split_number=10,
            radius="50%",  # 表盘大小
            center=[f"{y}%", f"{x}%"],  # 图表位置
            detail_label_opts=opts.LabelOpts(
                formatter="{value}",
                font_size=12
            ),
            min_=min_value,
            max_=max_value,
            start_angle=start_angle,
            end_angle=end_angle,
            title_label_opts=opts.LabelOpts(
                font_size=10,
                color="blue",
                font_family="Microsoft YaHei"
            ),
        )
        .set_series_opts(

        axisline_opts=opts.AxisLineOpts(
            linestyle_opts=opts.LineStyleOpts(
                color=[
                    (0.3, "#99CCFF"),  # 0~30% 区间为浅蓝
                    (0.7, "#FFD700"),  # 30~70% 区间为金色
                    (1, "#ff0000")     # 70~100% 区间为红色
                ],
                width=12,
            )
        )
        )
        .set_global_opts(title_opts=opts.TitleOpts(title=""))
    )
    return gauge
# 创建三个仪表图
gauge1 = create_gauge_chart("湿度 %", 53, 0, 100, 225, 45, 50, 85)
gauge2 = create_gauge_chart("温度 ℃", 32, -15, 45, 225, -45, 50, 50)
gauge3 = create_gauge_chart("风力 km/h", 3, 0, 50, 145, -45, 50, 18)

# 获取每个图表的HTML片段
gauge1_html = gauge1.render_embed()
gauge2_html = gauge2.render_embed()
gauge3_html = gauge3.render_embed()

# 手动拼接HTML内容
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Gauge Charts</title>
    <style>
        .gauge-container {{
            width: 32%;  /* 稍微增加一点宽度 */
            height: 128px;  /* 提高高度避免被裁剪 */
            margin: 0 0.5%;  /* 减少水平间距 */
            display: inline-block;
            vertical-align: top;
        }}
        @media (max-width: 768px) {{
            .gauge-container {{
                width: 100%;
                margin: 10px 0;
            }}
        }}
    </style>
</head>
<body>
<div style="width: 100%; display: flex; justify-content: space-around; flex-wrap: wrap;">
        <div style="width: 30%; height: 100px;">
            {gauge1_html}
        </div>
        <div style="width: 30%; height: 100px;">
            {gauge2_html}
        </div>
        <div style="width: 30%; height: 100px;">
            {gauge3_html}
        </div>
    </div>
</body>
</html>
"""
# 写入HTML文件
with open('./MyComponentsScript/thw.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("HTML 文件已生成: thw.html")

# 设置Edge的无头模式
edge_options = EdgeOptions()
edge_options.add_argument("--headless")  # 无头模式，不打开浏览器窗口
edge_options.add_argument("--disable-gpu")
edge_options.add_argument("--no-sandbox")

driver = webdriver.Edge(options=edge_options)

# 获取当前脚本所在目录，并构造HTML文件的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
html_path = os.path.join(current_dir, "MyComponentsScript", "thw.html")

# 打开本地HTML文件
driver.get(f"file:///{html_path}")

# 等待页面加载完成（可选，根据图表加载速度调整）
driver.implicitly_wait(5)

# 获取整个页面的高度并设置窗口大小
page_height = driver.execute_script("return document.body.scrollHeight")
driver.set_window_size(1920, page_height + 100)

# 截图并保存为PNG文件
driver.save_screenshot("thw_gauge.png")

# 关闭浏览器
driver.quit()

print("PNG 文件已生成: thw_gauge.png")
