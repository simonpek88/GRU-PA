# coding utf-8
import requests

from commFunc import gen_jwt


def get_weather(city_code, query_type, query_date=None):
    jwt_token = gen_jwt()
    headers = {
        'Authorization': f'Bearer {jwt_token}'
    }
    if query_type == 'lives':
        response = requests.get(f'https://kq359en4pj.re.qweatherapi.com/v7/weather/now?location={city_code}', headers=headers)
    elif query_type == 'historical':
        response = requests.get(f'https://kq359en4pj.re.qweatherapi.com/v7/historical/weather?location={city_code}&date={query_date}', headers=headers)

    data = response.json()
    #print(data)

    return data


def get_city_history_weather(city_code, query_date=None):
    try:
        city_weather_info = get_weather(city_code, 'historical', query_date)

        # 检查状态码
        if city_weather_info.get('code') == '200':
            history_data = city_weather_info['weatherDaily'] if city_weather_info.get('weatherDaily') else None
            history_data_hourly = city_weather_info['weatherHourly'] if city_weather_info.get('weatherHourly') else None
            print(history_data_hourly)

            if history_data:
                # 提取数据
                sunrise = history_data["sunrise"]
                sunset = history_data["sunset"]
                moonrise = history_data["moonrise"]
                moonset = history_data["moonset"]
                moonPhase = history_data["moonPhase"]
                tempMax = history_data["tempMax"]
                tempMin = history_data["tempMin"]
                humidity = history_data["humidity"]
                pressure = history_data["pressure"]

                WEATHERICON = {'多云': '☁️', '阴': '⛅', '小雨': '🌦️', '中雨': '🌧️', '大雨': '🌧️', '暴雨': '🌧️💧', '雷阵雨': '⛈️', '小雪': '🌨️',
                            '中雪': '❄️🌨', '大雪': '🌨❄️🌨', '暴雪': '❄️🌨❄️', '晴': '☀️', '雾': '🌫️', '霾': '🌫️', '风': '💨', '雪': '🌨️',
                            '冰雹': '🌨️', '冻雨': '❄️', '沙尘暴': '🌪️'}

                # 根据月相值插入对应的图标
                if moonPhase == '新月':
                    moon_icon = '🌑'
                elif moonPhase == '蛾眉月':
                    moon_icon = '🌒'
                elif moonPhase == '上弦月':
                    moon_icon = '🌓'
                elif moonPhase == '盈凸月':
                    moon_icon = '🌔'
                elif moonPhase == '满月':
                    moon_icon = '🌕'
                elif moonPhase == '亏凸月':
                    moon_icon = '🌖'
                elif moonPhase == '下弦月':
                    moon_icon = '🌗'
                elif moonPhase == '残月':
                    moon_icon = '🌘'
                else:
                    moon_icon = '🌙'

                temperature_dig = int(tempMax)
                # 根据温度选择体感图标
                if temperature_dig < 10:
                    temp_icon = '❄️ 寒冷'
                elif 10 <= temperature_dig <= 25:
                    temp_icon = '🌡️ 舒适'
                elif 26 <= temperature_dig <= 35:
                    temp_icon = '⚠️ 较热'
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

                temp_pack, weather_pack, precip_pack, windir_pack, windscale_pack, windspeed, humidity_pack, pressure_pack, weather_icon_pack = [], [], [], [], [], [], [], [], []
                if history_data_hourly:
                    for each in history_data_hourly:
                        temp_pack.append(each['temp'])
                        weather_pack.append(each['text'])
                        precip_pack.append(each['precip'])
                        windir_pack.append(each['windDir'])
                        windscale_pack.append(each['windScale'])
                        windspeed.append(each['windSpeed'])
                        humidity_pack.append(each['humidity'])
                        pressure_pack.append(each['pressure'])
                        weather_icon_pack.append(WEATHERICON[each['text']])

                return {
                    'sunrise': sunrise,
                    'sunset': sunset,
                    'moonrise': moonrise,
                    'moonset': moonset,
                    'moonPhase': moonPhase,
                    'tempMax': tempMax,
                    'tempMin': tempMin,
                    'humidity': humidity,
                    'pressure': pressure,
                    'moon_icon': moon_icon,
                    'temp_icon': temp_icon,
                    'humidity_icon': humidity_icon,
                    'temp_hourly': '/'.join(temp_pack),
                    'weather_hourly': '/'.join(weather_pack),
                    'precip_hourly': '/'.join(precip_pack),
                    'windir_hourly': '/'.join(windir_pack),
                    'windscale_hourly': '/'.join(windscale_pack),
                    'windspeed_hourly': '/'.join(windspeed),
                    'humidity_hourly': '/'.join(humidity_pack),
                    'pressure_hourly': '/'.join(pressure_pack),
                    'weather_icon_hourly': '/'.join(weather_icon_pack)
                }

    except Exception as e:
        # 异常处理
        print(f"Error fetching weather data: {e}")

    return None
