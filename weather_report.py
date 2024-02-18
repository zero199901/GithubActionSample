import os
import requests
import json
from bs4 import BeautifulSoup

# 从测试号信息获取
appID = os.environ.get("APP_ID")
appSecret = os.environ.get("APP_SECRET")
# 收信人ID即 用户列表中的微信号
openId = os.environ.get("OPEN_ID")
# 天气预报模板ID
weather_template_id = os.environ.get("TEMPLATE_ID")



def get_weather(my_city):
    # 天气预报链接列表
    urls = [
        "http://www.weather.com.cn/textFC/hb.shtml",  # 华北地区天气预报
        "http://www.weather.com.cn/textFC/db.shtml",  # 东北地区天气预报
        "http://www.weather.com.cn/textFC/hd.shtml",  # 华东地区天气预报
        "http://www.weather.com.cn/textFC/hz.shtml",  # 华中地区天气预报
        "http://www.weather.com.cn/textFC/hn.shtml",  # 华南地区天气预报
        "http://www.weather.com.cn/textFC/xb.shtml",  # 西北地区天气预报
        "http://www.weather.com.cn/textFC/xn.shtml"   # 西南地区天气预报
    ]

    for url in urls:
        resp = requests.get(url)
        text = resp.content.decode("utf-8")
        soup = BeautifulSoup(text, 'html5lib')
        div_conMidtab = soup.find("div", class_="conMidtab")
        tables = div_conMidtab.find_all("table")

        for table in tables:
            trs = table.find_all("tr")[2:]

            for index, tr in enumerate(trs):
                tds = tr.find_all("td")
                city_td = tds[-8]  # 城市所在的td元素

                this_city = list(city_td.stripped_strings)[0]

                if this_city == my_city:
                    high_temp_td = tds[-5]  # 最高温度所在的td元素
                    low_temp_td = tds[-2]   # 最低温度所在的td元素
                    weather_type_day_td = tds[-7]  # 白天天气类型所在的td元素
                    weather_type_night_td = tds[-4]  # 夜间天气类型所在的td元素
                    wind_td_day = tds[-6]  # 白天风向风力所在的td元素
                    wind_td_day_night = tds[-3]  # 夜间风向风力所在的td元素

                    high_temp = list(high_temp_td.stripped_strings)[0]
                    low_temp = list(low_temp_td.stripped_strings)[0]
                    weather_typ_day = list(weather_type_day_td.stripped_strings)[0]
                    weather_type_night = list(weather_type_night_td.stripped_strings)[0]

                    wind_day = list(wind_td_day.stripped_strings)[0] + list(wind_td_day.stripped_strings)[1]
                    wind_night = list(wind_td_day_night.stripped_strings)[0] + list(wind_td_day_night.stripped_strings)[1]

                    # 如果没有白天的数据就使用夜间的
                    temp = f"{low_temp}——{high_temp}摄氏度" if high_temp != "-" else f"{low_temp}摄氏度"
                    weather_typ = weather_typ_day if weather_typ_day != "-" else weather_type_night
                    wind = f"{wind_day}" if wind_day != "--" else f"{wind_night}"

                    return this_city, temp, weather_typ, wind


def get_access_token():
    # 获取access token的URL
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}'.format(appID.strip(), appSecret.strip())
    response = requests.get(url).json()
    access_token = response.get('access_token')
    return access_token


def get_daily_love():
    # 每日一句情话的API链接
    url = "https://api.lovelive.tools/api/SweetNothings/Serialization/Json"
    r = requests.get(url)
    all_dict = json.loads(r.text)
    sentence = all_dict['returnObj'][0]
    daily_love = sentence
    return daily_love

def send_weather(access_token, weather, openIds):
    # 发送天气预报给指定的openIds
    url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}'.format(access_token.strip())
    import datetime
    today = datetime.date.today()
    today_str = today.strftime("%Y年%m月%d日")
    for openId in openIds:
        payload = {
            "touser": openId.strip(),
            "template_id": weather_template_id.strip(),
            "data": {
                "date": {
                    "value": today_str
                },
                "region": {
                    "value": weather[0]
                },
                "weather": {
                    "value": weather[2]
                },
                "temp": {
                    "value": weather[1]
                },
                "wind_dir": {
                    "value": weather[3]
                },
                "today_note": {
                    "value": get_daily_love()
                }
            }
        }
        response = requests.post(url, json=payload)
        result = response.json()
        if result.get('errcode') == 0:
            print(f"天气预报发送成功给 {openId}")
        else:
            print(f"天气预报发送失败给 {openId}")

# 调用示例
access_token = get_access_token()
weather = get_weather('北京')
openIds = os.environ.get("OPEN_ID")
openIds = openIds.split(",")
send_weather(access_token, weather, openIds)