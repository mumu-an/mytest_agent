from typing import Any
from langchain.tools import tool
import base64
import requests

@tool
def get_task_id(user_name: str, user_count: int, mode: str="12,16"):
    """
    创建雀魂(Majsoul)玩家rating分析任务。

    参数:
    - user_name: 玩家昵称
    - user_count: 最近对局数量
    - mode: 分析模式
    """
    url = "http://localhost:29507/motrol/submit"

    payload = {
        "user_name": user_name,
        "user_count": user_count,
        "mode": mode
    }
    headers = {
        'Token': 'mumu',
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        return {
            "type": "error",
            "msg": "麻将maj rating的任务ID请求失败"
        }

    return {"type": "task","data": response.json()}

@tool
def get_rating_img(task_id: str):
    """
    查询rating任务结果（进度/图表/图片）

    参数:
    - task_id: 玩家完整的任务ID，必须原样传递。例如: 小诗乃_10_1782117741919305500，不要只传后面的数字。
    """
    url = f"http://localhost:29507/result/{task_id}"
    headers = {
        'Token': 'mumu'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 201:
        return {
            "type": "progress",
            "data": response.json()
        }
    elif response.status_code != 200:
        return {
            "type": "error",
            "msg": "请求失败"
        }

    return {
        "type": "image",
        "data": base64.b64encode(response.content).decode()
    }

@tool
def delete_task_id(task_id: str):
    """
    删除rating任务

    参数:
    - task_id: 任务ID
    """
    url = f"http://localhost:29507/task_delete/{task_id}"
    headers = {
        'Token': 'mumu'
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {
            "type": "error",
            "msg": "删除失败"
        }

    return {
        "type": "delete",
        "data": response.json()
    }

@tool
def get_paipu_task_id(paipu_id: str):
    """
    根据牌谱ID创建rating分析任务

    参数:
    - paipu_id: 牌谱ID
    """
    url = "http://localhost:29507/motrol/submit_paipu"

    payload = {
        "paipu_id": paipu_id
    }
    headers = {
        'Token': 'mumu',
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        return {
            "type": "error",
            "msg": "创建失败"
        }

    return {
        "type": "task",
        "data": response.json()
    }


if __name__ == "__main__":
    raw_data = get_task_id.invoke({"user_name":"scfffq","user_count":20,"mode":"9,12,16"})
    raw_data = get_rating_img.invoke({"task_id":"scfffq_20_1781578300252265811"})
    print(raw_data)