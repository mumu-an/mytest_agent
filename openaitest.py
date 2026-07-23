from langchain.agents import create_agent
from langchain.tools import tool
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import requests
# 加载 .env 文件（默认在当前目录查找）
load_dotenv()


#  定义工具：让模型知道它能调这个函数
@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气"""

    # 模拟天气情况，实际项目中调用天气API
    return f"{city}今天的天气阴转多云，气温30°C"

@tool
def get_wttr(city: str) -> str:
    """获取 wttr 天气原始JSON数据"""

    url = f"https://wttr.in/{city}?format=j1"
    resp = requests.get(url)

    if resp.status_code != 200:
        return "天气接口请求失败"

    return resp.text   # ⚠️ 只返回原始数据，不做分析


# 初始化模型，可以选择之前介绍3种方法中任意一种来构建
llm = init_chat_model(
    model="google_genai:gemini-2.5-flash",  # 模型名称
)

# 创建Agent
agent = create_agent(model=llm, tools=[get_weather, get_wttr])  # 模型  # 可用工具列表

response = agent.invoke({"messages": [{"role": "user", "content": "根据 wttr 的数据厦门的天气怎么样"}]})
print(f"【问题4】：{response['messages'][-1].text}")