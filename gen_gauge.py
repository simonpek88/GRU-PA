from pyecharts import options as opts
from pyecharts.charts import Gauge


def create_gauge_chart(name, value, min_value, max_value, start_angle, end_angle):
    gauge = (
        Gauge()
        .add(
            "",
            [(name, value)],
            split_number=10,
            radius="70%",
            detail_label_opts=opts.LabelOpts(formatter="{value}"),
            min_=min_value,
            max_=max_value,
            start_angle=start_angle,
            end_angle=end_angle,
            title_label_opts=opts.LabelOpts(
                font_size=20, color="blue", font_family="Microsoft YaHei"
            ),
        )
        .set_global_opts(title_opts=opts.TitleOpts(title=""))
    )
    return gauge

# 创建三个仪表图
gauge1 = create_gauge_chart("温度 ℃", 36, -15, 45, 225, 45)
gauge2 = create_gauge_chart("湿度 %", 53, 0, 100, 225, -45)
gauge3 = create_gauge_chart("风力 km/h", 3, 0, 50, 145, -45)

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
</head>
<body>
    <div style="width: 100%; display: flex; justify-content: space-around; flex-wrap: wrap;">
        <div style="width: 30%;">
            {gauge1_html}
        </div>
        <div style="width: 30%;">
            {gauge2_html}
        </div>
        <div style="width: 30%;">
            {gauge3_html}
        </div>
    </div>
</body>
</html>
"""

# 写入HTML文件
with open('./temp_humidity_windspeed_gauge.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("HTML 文件已生成: temp_humidity_windspeed_gauge.html")