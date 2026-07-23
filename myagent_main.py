# -*- coding: UTF-8 -*-
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from othertool.mytool import MyLogger
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain.chat_models import init_chat_model
from api_method import rating_fastapi
from pydantic import BaseModel
import asyncio
from aitool.weather_tool import *
from aitool.maj_tool import *
from fastapi import FastAPI
from fastapi import Request
import time
import os
from datetime import datetime
from fastapi.staticfiles import StaticFiles
import uvicorn
from fastapi.middleware.cors import CORSMiddleware



load_dotenv()  # 会自动读取 .env 文件
logger = MyLogger("fast_api_log", log_file=f"./log/fask_api.log", max_log_size=1024 * 1024 * 9, backup_count=10)


app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发阶段
    allow_methods=["*"],
    allow_headers=["*"],
)

class Master:
    def __init__(self):
        self.mode_name = "google_genai:gemini-2.5-flash"
        self.llm = init_chat_model(
            model=self.mode_name,  # 模型名称
        )
        tools = [get_wttr_weather, get_task_id, get_rating_img, delete_task_id, get_paipu_task_id]

        # 关键：先 bind_tools
        # 关键：先把 tools 绑定到模型上
        self.llm_with_tools = self.llm.bind_tools(tools)

        # 使用普通字符串作为 system_prompt（create_agent 要求的格式）
        self.SYSTEM_PROMPT = """你是麻将雀魂 rating 分析助手。
        【强制工具调用规则 - 必须严格遵守】

        用户输入只要包含以下任意特征，**立即调用对应工具，不要输出任何解释文字**：

        - 出现玩家昵称（如“小诗乃”） + “局” 或 “rating” 或 “战绩” 或 “任务ID”
          → 必须调用 get_task_id，user_count 默认用 10，mode 默认 "12,16"

        - 提到 “结果” “图表” “进度”
          → task_id **必须完整复制用户提供的字符串**，不要截断、不要只取数字部分
          → 调用 get_rating_img(task_id)

        - 提到 “删除” 或 “取消任务”
          → 调用 delete_task_id

        【重要回复原则】
        - **调用工具后，必须生成自然语言回复**，严禁直接把工具返回的原始JSON或大段数据返回给用户。
        - 只有在需要调用工具时才调用工具，工具执行完后自然语言回复。
        - 现在需要你额外提供回复内容的情绪，例如neutral, friendly, explanatory, comforting, excited等
        - 严格输出格式改为｛内容:"内容",情绪:"情绪"｝
        - 默认中文回答。
        """

        self.agent = create_agent(
            model=self.llm_with_tools,  # 使用 bind_tools 后的模型
            tools=tools,
            system_prompt=self.SYSTEM_PROMPT  # 必须是字符串！
        )


    async def chat(self, input):
        logger.info(f"开始处理用户输入: {input}")
        response = await self.agent.ainvoke({
            "messages": [HumanMessage(content=input)]
        })
        # ==================== 调试输出 ====================
        print("=== DEBUG: Agent Response ===")
        # print(response['messages'])
        messages = response['messages']

        tool_result = None
        ai_result = None

        for m in messages:

            name = m.__class__.__name__

            # ---------------- TOOL ----------------
            if name == "ToolMessage":

                content = m.content

                # string → dict
                if isinstance(content, str):
                    try:
                        import json
                        content = json.loads(content)
                    except:
                        pass

                if isinstance(content, dict):
                    tool_result = content

            # ---------------- AI ----------------
            if name == "AIMessage":
                if hasattr(m, "content") and isinstance(m.content, str):
                    if m.content.strip():
                        ai_result = m.content
                elif hasattr(m, "content") and isinstance(m.text, str):
                    if m.text.strip():
                        ai_result = m.text
        # =========================
        # 🎯 你的核心规则
        # =========================

        # 2️⃣ 没 AI → fallback tool（结果）
        if tool_result:
            # 图片直接返回
            if tool_result.get("type") == "image":
                return tool_result

        # 1️⃣ 有 AI → 优先 AI（解释）
        if ai_result:
            return {
                "type": "text",
                "data": ai_result
            }

        # 3️⃣ 都没有
        return {
            "type": "error",
            "msg": "empty response"
        }
        # return response['messages'][-1].text

master = Master()
# =========================
# rating 服务启动
# =========================
async def start_background():
    asyncio.create_task(rating_fastapi.main())


# 接管日记格式的
@app.middleware("http")
async def request_log_middleware(request: Request, call_next):
    """日记打印请求接口时间"""
    start = time.time()

    response = await call_next(request)

    cost_ms = round((time.time() - start) * 1000, 2)
    # 根据状态码选择日志方法
    if response.status_code >= 500:
        log_func = logger.error   # 服务器错误
    elif response.status_code >= 400:
        log_func = logger.warning # 客户端错误
    else:
        log_func = logger.info    # 成功请求

    log_func(
        "method=%-8s | status=%-4s | cost_ms=%-8.2f | path=%s | client=%s",
        request.method,
        response.status_code,
        cost_ms,
        request.url.path,
        request.client.host if request.client else "-"
    )

    return response

# ====================== 静态文件配置 ======================
STATIC_DIR = "./static/rating_images"
os.makedirs(STATIC_DIR, exist_ok=True)
SERVER_HOST = "http://localhost:29506"   # ← 这里改成你的实际域名或IP
app.mount("/rating_images", StaticFiles(directory=STATIC_DIR), name="rating_images")

def save_image_and_get_url(image_bytes: bytes, task_id: str = "rating") -> str:
    """保存图片并返回URL"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{task_id}_{timestamp}.png"
    file_path = os.path.join(STATIC_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(image_bytes)

    return f"{SERVER_HOST}/rating_images/{filename}"

# ====================== 本地聊天网页 ======================
CHAT_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>雀魂 Rating 助手</title>
    <style>
        body { font-family: 'Microsoft YaHei', Arial; margin:0; padding:0; background: #f0f2f5; }
        #chat { max-width: 800px; margin: 20px auto; background: white; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); height: 85vh; display: flex; flex-direction: column; }
        #messages { flex: 1; padding: 20px; overflow-y: auto; }
        .message { margin: 10px 0; padding: 12px 15px; border-radius: 10px; max-width: 80%; }
        .user { background: #1890ff; color: white; margin-left: auto; border-bottom-right-radius: 2px; }
        .assistant { background: #f1f1f1; margin-right: auto; border-bottom-left-radius: 2px; }
        img { max-width: 100%; border-radius: 8px; margin-top: 8px; }
        #input-area { padding: 15px; border-top: 1px solid #ddd; display: flex; }
        #user-input { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 16px; }
        button { margin-left: 10px; padding: 0 25px; background: #1890ff; color: white; border: none; border-radius: 8px; cursor: pointer; }
    </style>
</head>
<body>
    <div id="chat">
        <div id="messages"></div>
        <div id="input-area">
            <input type="text" id="user-input" placeholder="输入玩家昵称、任务ID、战绩、图表等...">
            <button onclick="sendMessage()">发送</button>
        </div>
    </div>

    <script>
        const messagesDiv = document.getElementById('messages');
        const input = document.getElementById('user-input');

        async function sendMessage() {
            const text = input.value.trim();
            if (!text) return;

            addMessage('user', text);
            input.value = '';

            const response = await fetch('/agent/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({input: text})
            });

            const res = await response.json();
            const data = res.data;
            
            if (data && data.type === 'image') {
                addMessage('assistant', `
                    <div style="margin-bottom:8px;">✅ 已为您查询到该任务的 rating 分析结果，图表如下：</div>
                    <img src="${data.url}" alt="rating图表" style="max-width:100%; border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,0.1);">
                `);
            } else {
                addMessage('assistant', data.content || '收到回复');
            }
        }

        function addMessage(role, content) {
            const div = document.createElement('div');
            div.className = `message ${role}`;
            div.innerHTML = content;
            messagesDiv.appendChild(div);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        // 支持回车发送
        input.addEventListener('keypress', e => { if (e.key === 'Enter') sendMessage(); });
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def home():
    return CHAT_HTML

class ChatRequest(BaseModel):
    input: str


@app.post("/agent/chat")
async def chat(req: ChatRequest):
    # logger.info(f"接收用户询问：{req.input}, ")
    raw = await master.chat(input=req.input)
    # 1️⃣ 非 dict 直接返回
    if not isinstance(raw, dict):
        return {
            "status": "success",
            "data": {
                "type": "text",
                "content": str(raw)
            }
        }

    t = raw.get("type")

    # ---------------- IMAGE ----------------
    if t == "image":
        task_id = "unknown"
        if isinstance(req.input, str):
            parts = req.input.split()
            for p in parts:
                if "_" in p and len(p) > 10:
                    task_id = p
                    break

        image_bytes = base64.b64decode(raw["data"])
        image_url = save_image_and_get_url(image_bytes, task_id)

        return {
            "status": "success",
            "data": {
                "type": "image",
                "url": image_url
            }
        }

    # ---------------- PROGRESS ----------------
    if t == "progress":
        return {
            "status": "success",
            "data": {
                "type": "progress",
                "content": raw["data"]
            }
        }

    # ---------------- TASK ----------------
    if t == "task":
        return {
            "status": "success",
            "data": {
                "type": "task",
                "content": raw["data"]
            }
        }

    # ---------------- DELETE ----------------
    if t == "delete":
        return {
            "status": "success",
            "data": {
                "type": "delete",
                "content": raw["data"]
            }
        }

    # ---------------- ERROR ----------------
    if t == "error":
        return {
            "status": "error",
            "content": raw.get("msg", "unknown error")
        }

    # ---------------- TEXT fallback ----------------
    return {
        "status": "success",
        "data": {
            "type": "text",
            "content": raw["data"]
        }
    }



# =========================
# 启动 uvicorn
# =========================
async def run_server():
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=29506,
        access_log=False
    )
    server = uvicorn.Server(config)
    await server.serve()


# =========================
# 主入口
# =========================
async def main():
    await start_background()
    # # 可选：测试 agent
    # print(await master.chat("根据 wttr 的数据广州番禺的天气怎么样"))

    await run_server()

if __name__ == "__main__":
    asyncio.run(main())
