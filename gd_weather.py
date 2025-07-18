# coding utf-8
import re

import requests

from commFunc import getEncryptKeys


def get_weather(city_code):
    gd_key = getEncryptKeys('gd_key')
    url = 'https://restapi.amap.com/v3/weather/weatherInfo?parameters'
    params_realtime = {
        'key':gd_key,
        'city':city_code,
        'extensions':'base'
    }
    params_estimate = {
        'key':gd_key,
        'city':city_code,
        'extensions':'all'
    }

    res = requests.get(url=url,params=params_realtime) # 实时天气
    #res = requests.get(url=url,params=params_estimate) # 预报天气
    weather_info = res.json()

    return weather_info


def get_city_weather(city_code):
    try:
        city_weather_info = get_weather(city_code)

        # 检查状态码
        if city_weather_info.get('status') == '1':
            # 直接获取天气信息，不需要使用.get()因为已经是字典了
            live_data = city_weather_info['lives'][0] if city_weather_info.get('lives') else None

            if live_data:
                # 提取数据
                province = live_data["province"]  # 获取省份
                city = live_data["city"]  # 获取城市
                adcode = live_data["adcode"]  # 获取城市编码
                reporttime = live_data["reporttime"]  # 获取发布数据时间
                weather = live_data["weather"]  # 天气现象
                temperature = live_data["temperature"]  # 温度
                winddirection = live_data["winddirection"]  # 风向
                windpower = live_data["windpower"]  # 风力
                humidity = live_data["humidity"]  # 湿度

                WEATHERICON = {'多云': '☁️', '阴': '⛅', '小雨': '🌦️', '中雨': '🌧️', '大雨': '🌧️', '暴雨': '🌧️💧', '阵雨': '🌦️', '雷阵雨': '⛈️', '小雪': '🌨️',
                            '中雪': '❄️🌨', '大雪': '🌨❄️🌨', '暴雪': '❄️🌨❄️', '晴': '☀️', '雾': '🌫️', '霾': '🌫️', '风': '💨', '雪': '🌨️',
                            '冰雹': '🌨️', '冻雨': '❄️', '沙尘暴': '🌪️'}
                if weather in WEATHERICON:
                    weather_icon = WEATHERICON[weather]
                else:
                    weather_icon = '🚫'

                # 使用正则表达式提取数字部分
                wind_power_dig = re.search(r'\d+', windpower)
                if wind_power_dig:
                    wind_power_dig = int(wind_power_dig.group())
                else:
                    wind_power_dig = 0
                # 根据风力强度选择图标
                if wind_power_dig < 5:
                    wind_icon = '🍃 微风'
                elif 5 <= wind_power_dig < 10:
                    wind_icon = '🌬️ 轻风'
                elif 10 <= wind_power_dig < 20:
                    wind_icon = '🌬️ 和风'
                elif 20 <= wind_power_dig < 30:
                    wind_icon = '💨 强风'
                elif 30 <= wind_power_dig < 40:
                    wind_icon = '🌪️ 大风'
                else:
                    wind_icon = '🌀 暴风'

                temperature_dig = int(temperature)
                # 根据温度选择体感图标
                if temperature_dig < 10:
                    temp_icon = '❄️ 寒冷'
                elif 10 <= temperature_dig <= 25:
                    temp_icon = '🌿 舒适'
                elif 26 <= temperature_dig <= 35:
                    temp_icon = '🥵 较热'
                else:
                    temp_icon = '🔥 高温'

                humidity_dig = int(humidity)
                # 根据湿度选择图标
                if humidity_dig < 40:
                    humidity_icon = '🌵 干燥'
                elif 40 <= humidity_dig <= 70:
                    humidity_icon = '💧 舒适'
                else:
                    humidity_icon = '💦 潮湿'

                return {
                    'province': province,
                    'city': city,
                    'adcode': adcode,
                    'reporttime': reporttime,
                    'weather': weather,
                    'temperature': temperature,
                    'winddirection': winddirection,
                    'windpower': windpower,
                    'humidity': humidity,
                    'weather_icon': weather_icon,
                    'wind_icon': wind_icon,
                    'temp_icon': temp_icon,
                    'humidity_icon': humidity_icon
                }
            else:
                return None
        else:
            return None
    except Exception as e:
        # 异常处理
        print(f"无法获取数据: {e}")

    return None
