import requests
from langchain.tools import tool


@tool
def get_wttr_weather(city: str) -> str:
    """获取 wttr 天气原始JSON数据"""

    url = f"https://wttr.in/{city}?format=j1"
    response = requests.get(url)

    if response.status_code != 200:
        return "天气接口请求失败"

    return response.json()   # ⚠️ 只返回原始数据，不做分析


if __name__ == "__main__":
    city = "番禺"
    raw_data = get_wttr_weather.invoke({"city": city})
    print(raw_data)