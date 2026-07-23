import asyncio
import copy
import json
import time
import base64
from api_method.maj_method import AmaeKoromo, Motrol
from othertool.conredis import AsyncRedisTool
from othertool.mytool import logger
from api_method.chrome_get_token import chrome_get_token_main
from api_method import get_image

class RatingManager:

    def __init__(self):
        self.task_queue = asyncio.Queue()
        self.results = {}
        self.redis = AsyncRedisTool(db=8)
        self.motrol = Motrol()

    async def start(self):
        """
        整个程序只启动一次
        """
        asyncio.create_task(
            chrome_get_token_main()
        )

        asyncio.create_task(
            self.fetch_tasks_from_redis()
        )

        asyncio.create_task(
            self.scheduler()
        )

        asyncio.create_task(
            self.save_redis_result()
        )

    async def fetch_tasks_from_redis(self):

        while True:

            task_id = await self.redis.pop("get_json")

            if not task_id:
                await asyncio.sleep(1)
                continue
            task = copy.deepcopy(task_id)
            rating = self.motrol.get_rating(
                task["agent"],
                task["cookie"],
                task["task_id"]
            )
            result_key = task["result_key"]
            if rating is not None:
                if result_key not in self.results:
                    break
                self.results[result_key]["data"][task['paipu']]["rating"] = rating
                self.results[result_key]["finished"] += 1
                if self.results[result_key]["finished"] == self.results[result_key]["total"]:
                    avg_rating = (
                            sum(
                                values["rating"]
                                for paipu, values in self.results[result_key]["data"].items()
                            )
                            / self.results[result_key]["total"]
                    )
                    self.results[result_key]["avg_rating"] = round(
                        avg_rating,
                        2
                    )
                    self.results[result_key]["status"] = "finished"
                    self.results[result_key]["end_time"] = time.strftime("%Y-%m-%d %H:%M:%S",
                                                                         time.localtime(time.time()))
            else:
                await self.task_queue.put(
                    {
                        "task_id": task_id,
                        "execute_at": time.time() + 180
                    }
                )
                self.results[task_id["result_key"]]["progress"] += 1
                self.results[task_id["result_key"]]["progress_endtime"] = time.time() + 180
                await asyncio.sleep(0.5)

    async def scheduler(self):



        while True:

            item = await self.task_queue.get()

            task = item["task_id"]

            # 1️⃣ 等待到执行时间
            now = time.time()
            delay = item["execute_at"] - now
            if delay > 0:
                await asyncio.sleep(delay)

            logger.info(f"开始处理 {task}")
            result_key = task["result_key"]
            # 2️⃣ 轮询获取结果（未出结果则每5秒重试）
            while True:
                # result_key_result = self.results.get(result_key)
                rating = self.motrol.get_rating(
                    task["agent"],
                    task["cookie"],
                    task["task_id"]
                )

                if rating is not None:
                    if result_key not in self.results:
                        break
                    self.results[result_key]["data"][task['paipu']]["rating"] = rating
                    self.results[result_key]["finished"] += 1
                    if self.results[result_key]["finished"] == self.results[result_key]["total"]:
                        avg_rating = (
                                sum(
                                    values["rating"]
                                    for paipu, values in self.results[result_key]["data"].items()
                                )
                                / self.results[result_key]["total"]
                        )
                        self.results[result_key]["avg_rating"] = round(
                                avg_rating,
                                2
                            )
                        self.results[result_key]["status"] = "finished"
                        self.results[result_key]["end_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    break

                # 3️⃣ 没结果 → 等5秒继续查
                await asyncio.sleep(5)
            await asyncio.sleep(1)

    async def submit_task(
            self,
            user_name,
            user_count,
            mode
    ):

        mode_dict = {
            "金": "9",
            "玉": "12",
            "王": "16"
        }

        if mode in mode_dict.keys():
            mode = mode_dict[mode]

        amae = AmaeKoromo()

        user_id = amae.search_player_id(user_name)
        if not user_id:
            return None

        if not user_count:
            user_count = amae.search_player_msg(user_id, mode)

        user_motrol_id = amae.get_motroplayid(
            user_id
        )

        user_uuids_dict = amae.get_historydata(
            player_id=user_id,
            limit=user_count,
            mode=mode
        )

        task_id = f"{user_name}_{user_count}_{time.time_ns()}"

        result_dict = {}

        redis_tasks = []

        for uuid, value in user_uuids_dict.items():

            paipu = f"{uuid}_a{user_motrol_id}"

            result_dict[paipu] = {
                "rating": None,
                "score": value["score"]
            }

            redis_tasks.append(
                self.redis.push(
                    "get_token_result",
                    {
                        "paipu": paipu,
                        "result_key": task_id
                    }
                )
            )

        self.results[task_id] = {
            "status": "pending",
            "total": len(result_dict),
            "finished": 0,
            "data": result_dict,
            "create_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        }

        await asyncio.gather(*redis_tasks)

        return task_id


    async def submit_paipu(
            self,
            paipu_id
    ):
        user_id = paipu_id.split("_a")
        if len(user_id) == 1:
            return None
        paipu_uuid  = user_id[0]

        mode = "9,12,16"
        amae = AmaeKoromo()
        user_motrol_id = int(user_id[1])
        user_id  = amae.get_player_id(user_motrol_id)
        user_count = amae.search_player_msg(user_id, mode)



        user_uuids_dict = amae.get_historydata(
            player_id=user_id,
            limit=user_count,
            mode=mode,
            paipu_uuid=paipu_uuid
        )
        if not user_uuids_dict:
            user_uuids_dict = {
                        paipu_uuid: {
                            "score": 0
                        }
                    }
        task_id = f"{paipu_id}_{time.time_ns()}"

        result_dict = {}

        redis_tasks = []

        for uuid, value in user_uuids_dict.items():

            paipu = f"{uuid}_a{user_motrol_id}"

            result_dict[paipu] = {
                "rating": None,
                "score": value["score"]
            }

            redis_tasks.append(
                self.redis.push(
                    "get_token_result",
                    {
                        "paipu": paipu,
                        "result_key": task_id
                    }
                )
            )

        self.results[task_id] = {
            "status": "pending",
            "total": len(result_dict),
            "finished": 0,
            "data": result_dict,
            "create_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        }

        await asyncio.gather(*redis_tasks)
        return task_id



    def get_result(self, task_id):
        return self.results.get(task_id)

    async def delete_task_result(self, task_id):
        delete_list = self.results.get(task_id)
        delete_list_data = delete_list.get("data",[])
        get_token_result_delete = [{"paipu": paipu,"result_key": task_id} for paipu in delete_list_data.keys()]
        for task in get_token_result_delete:
            await self.redis.redis.lrem(
                "get_token_result",
                1,
                json.dumps(task)
            )

        self.results.pop(task_id, None)
        return await self.redis.redis.delete(task_id)



    async def save_redis_result(self):
        while True:
            to_delete = []

            for key in list(self.results.keys()):
                value = self.results[key]

                # =========================
                # ⭐ 1. finished（只执行一次）
                # =========================
                if value["status"] == "finished":
                    image_bytes = await asyncio.to_thread(
                        get_image.plot_rating_score,
                        value['data'],
                        name=key.split('_')[0]
                    )
                    value['image_bytes'] = base64.b64encode(image_bytes).decode()
                    await self.redis.redis.set(
                        key,
                        json.dumps(value, ensure_ascii=False),
                        ex=3600
                    )

                    to_delete.append(key)
                    continue
                # =========================
                # ⭐ pending / running（只看 finished 变化）
                # =========================
                current_finished = value.get("finished", 0)
                current_progress = value.get("progress", 0)
                total = value.get("total", 1)

                # ⭐ 用 finished 作为“变化触发器”
                if value.get("last_finished") != current_finished or value.get("progress") != current_progress:
                    value["last_finished"] = current_finished
                    value["progress"] = current_progress
                    await self.redis.redis.set(
                        key,
                        json.dumps(value, ensure_ascii=False),
                        ex=3600
                    )

            # =========================
            # ⭐ 3. 清理 finished
            # =========================
            for k in to_delete:
                self.results.pop(k, None)

            await asyncio.sleep(5)