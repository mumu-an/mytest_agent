import asyncio
import time
import json
import uvicorn
import base64
from fastapi import FastAPI
from othertool.mytool import logger
from pydantic import BaseModel
from api_method.rating_manager import RatingManager
from fastapi.responses import Response, JSONResponse
from fastapi import Request


manager = RatingManager()
app = FastAPI(
    # docs_url=None,
    # redoc_url=None,
    # openapi_url=None,
)
API_TOKEN = "mumu"

# 接管日记格式的
@app.middleware("http")
async def request_log_middleware(request: Request, call_next):
    """日记打印请求接口时间"""
    start = time.time()

    token = request.headers.get("Token")
    if request.url.path in ["/docs", "/openapi.json", "/redoc"]:
        return await call_next(request)
    elif token != f"{API_TOKEN}":
        return JSONResponse(
            {"error": "unToken"},
            status_code=401
        )

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


# -------------------------
# 请求模型
# -------------------------
class TaskReq(BaseModel):
    user_name: str
    user_count: int
    mode: str = "12,16"

class QueryModel(BaseModel):
    paipu_id: str

# -------------------------
# 提交任务接口
# -------------------------
@app.post("/motrol/submit")
async def submit(req: TaskReq):
    task_id = await manager.submit_task(
        user_name=req.user_name,
        user_count=req.user_count,
        mode=req.mode
    )
    if not task_id:
        return JSONResponse(
            {"task_id": task_id, "msg": f"找不到{req.user_name}该用户ID"},
            status_code=404
        )
    else:
        return JSONResponse(
            {"task_id": task_id, "msg": f"任务查询ID为 {task_id}，已经开始获取数据，请稍候。"},
            status_code=200
        )

# -------------------------
# 提交牌谱接口
# -------------------------
@app.post("/motrol/submit_paipu")
async def submit_paipu(req: QueryModel):
    task_id = await manager.submit_paipu(
        paipu_id=req.paipu_id
    )
    if not task_id:
        return JSONResponse(
            {"task_id": task_id, "msg": f"找不到该牌谱ID的指定参考玩家,可能确实_a后面的motrolid"},
            status_code=404
        )
    else:
        return JSONResponse(
            {"task_id": task_id, "msg": f"任务查询ID为 {task_id}，已经开始获取数据，请稍候。"},
            status_code=200
        )


# -------------------------
# 查询任务接口
# -------------------------
@app.get("/result/{task_id}")
async def result(task_id: str):
    raw = await manager.redis.redis.get(task_id)
    if not raw:
        return JSONResponse(
            {"error": "task not found"},
            status_code=404
        )
    res = json.loads(raw)
    if res["status"] != "finished":
        # ===== 进度数据 =====
        return JSONResponse(
            {
                "status": res.get("status"),
                "create_time": res.get("create_time"),
                "total": res.get("total"),
                "finished": res.get("finished"),
                "progress": res.get("progress"),
                "progress_end": res.get("progress_end"),
            },
            status_code=201
        )
    else:
        image_bytes = base64.b64decode(res['image_bytes'])
        return Response(
        content=image_bytes,
            media_type="image/png"
        )

# -------------------------
# 删除任务接口
# -------------------------
@app.get("/task_delete/{task_id}")
async def result(task_id: str):
    result = await manager.delete_task_result(task_id)
    if result:
        return JSONResponse(
            {
                "msg": f"已删除{task_id} 任务",
            },
            status_code=200
        )
    else:
        return JSONResponse(
            {
                "msg": f"该{task_id} 任务不存在",
            },
            status_code=404
        )



async def main():
    await manager.start()
    # 启动 FastAPI
    config = uvicorn.Config(app, host="0.0.0.0", port=29507,access_log=False)
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())