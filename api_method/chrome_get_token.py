import random
import asyncio
import os
from othertool.mytool import logger
from playwright.async_api import async_playwright, TimeoutError
from api_method.maj_method import Motrol
from chrome_utils.fingerprint_utils import generate_random_fingerprint
from othertool.conredis import AsyncRedisTool

class ChromeGetToken:
    def __init__(self, user_name="user_data"):
        self.playwright = None
        BASE_DIR = os.getcwd()
        self.CHROME_PATH = os.path.join(BASE_DIR, "fingerprint_browser", "chrome.exe")
        self.USER_DATA_DIR = os.path.join(BASE_DIR, "data", user_name)
        self.DEFAULT_WINDOW_SIZE = {"width": 1600, "height": 900}
        self.BROWSER_ARGS = [
            "--disable-blink-features=AutomationControlled",
            "--test-type",
            "--disable-non-proxied-udp",
            "--disable-features=ImprovedCookieControls",
            "--lang=zh-CN",
            "--accept-lang=zh-CN,zh;q=0.9",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-fre",
            f"--window-size={self.DEFAULT_WINDOW_SIZE['width']},{self.DEFAULT_WINDOW_SIZE['height']}"
        ]
        base_fp = generate_random_fingerprint()
        fp_args = {
            # 'fingerprint': '--fingerprint',
            'platform': '--fingerprint-platform',
            'platformVersion': '--fingerprint-platform-version',
            'brand': '--fingerprint-brand',
            'brandVersion': '--fingerprint-brand-version',
            'hardwareConcurrency': '--fingerprint-hardware-concurrency',
            'gpu_vendor': '--fingerprint-gpu-vendor',
            # 'gpu_renderer': '--fingerprint-gpu-renderer',
            'timezone': '--timezone',
            'userAgent': ''
        }
        for key, arg in fp_args.items():
            if key == "userAgent":
                self.userAgent = base_fp.get(key, "")
                continue
            if key in base_fp:
                self.BROWSER_ARGS.append(f"{arg}={base_fp[key]}")

    async def create_chrome(self):
        self.playwright = await async_playwright().start()
        context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.USER_DATA_DIR),
            executable_path=str(self.CHROME_PATH),
            headless=True,
            viewport=self.DEFAULT_WINDOW_SIZE,
            args=self.BROWSER_ARGS,
            ignore_default_args=["--enable-automation"],
            user_agent=self.userAgent
        )
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto("data:text/html,<title>tiktok</title>")
        return context, page, context.browser


    async def get_cloudtoken(self, page):
        while True:
            try:
                await page.goto("https://mjai.ekyu.moe/zh-cn.html", timeout=10000)
                cdp = await page.context.new_cdp_session(page)
            except TimeoutError:
                continue
            # 初始滚动
            total_scrolled = 0
            await page.mouse.wheel(0, 1150)

            # 模拟随机滚动到目标
            step = 50
            for _ in range(6):
                locator = page.locator("div.cf-turnstile")
                for i in range(await locator.count()):
                    box = await locator.nth(i).bounding_box()
                    x = box["x"] + box["width"] / 50
                    y = box["y"] + box["height"] / 2
                    await cdp.send("Input.dispatchMouseEvent", {
                        "type": "mouseMoved",
                        "x": x,
                        "y": y
                    })
                    await asyncio.sleep(0.5)
                await asyncio.sleep(random.uniform(1, 2))
                await page.mouse.wheel(0, step)
                total_scrolled += step
                step = random.randint(-30, 30)

                elements = await page.query_selector_all("input[name='cf-turnstile-response']")
                values = []
                for element in elements:
                    value_handle = await element.get_property("value")
                    cf_token = await value_handle.json_value()
                    if cf_token:
                        values.append(cf_token)

                if len(values) == 2:
                    break

            if values:
                await asyncio.sleep(random.uniform(1, 3))
                # 假设你已经有 page 对象
                cookies = await page.context.cookies()

                # 拼成标准 Cookie header
                cookie_header = "; ".join(f"{c['name']}={c['value']}" for c in cookies)
                return [{"token": value.strip(), "agent": self.userAgent, "cookie": cookie_header} for value in values]
            await asyncio.sleep(random.uniform(1, 2))


class TokenService:
    def __init__(self, aredis: AsyncRedisTool, count=10):
        self.max_workers = count
        self.redis = aredis
        self.lock = asyncio.Lock()           # 异步锁，确保并发安全
        self.motrol = Motrol()
        self.user_dir_pool = [f"user_data_{i}" for i in range(1, count + 1)]
        self.running_dirs = set()  # 正在被 worker 占用的目录
        self.active_workers = 0  # 当前活跃 worker 数

    async def _worker(self):
        """动态 worker 调度器，只有队列非空才启动 worker"""
        while True:
            # 先检查队列
            if not await self.redis.redis.llen("get_token_result"):
                await asyncio.sleep(0.5)  # 队列空了，等一会儿再看
                continue

            # 判断是否可以创建新 worker
            if self.active_workers >= self.max_workers:
                await asyncio.sleep(0.1)
                continue

            # 从池中找一个空闲的用户目录
            user_name = None
            async with self.lock:
                for dir_name in self.user_dir_pool:
                    if dir_name not in self.running_dirs:
                        user_name = dir_name
                        self.running_dirs.add(dir_name)
                        break

            if user_name is None:
                # 所有用户目录都在运行，等一下
                await asyncio.sleep(0.1)
                continue

            # 启动 worker
            asyncio.create_task(self.worker_task(user_name))
            logger.info(f"创建{user_name}并发")
            self.active_workers += 1

    async def get_next_uid(self):
        """统一从 token_queue 获取下一个 UID"""
        return await self.redis.pop("get_token_result", timeout=10)

    async def worker_task(self, user_name):
        """每个任务独立运行一个浏览器实例"""
        myChrome = ChromeGetToken(user_name)
        context, page, browser = await myChrome.create_chrome()
        try:
            while True:
                uid_dict = await self.get_next_uid()
                if not uid_dict:
                    break  # 队列空了

                paipu = uid_dict["paipu"]
                uid = paipu.split("_")[0]
                token = await myChrome.get_cloudtoken(page)
                task_id = self.motrol.get_taskport(token[0]['token'], token[0]['agent'], token[0]['cookie'], paipu)
                if task_id:
                    logger.info(f"uid：{uid}")
                    token[0]['paipu'] = paipu
                    token[0]['task_id'] = task_id
                    token[0]['result_key'] = uid_dict["result_key"]
                    await self.redis.push("get_json", token[0])
                else:
                    await self.redis.push_before("get_token_result", uid_dict)
                # 如果有第二个 token，再获取一个 UID 并推送
                if len(token) >= 2:
                    uid_dict2 = await self.get_next_uid()
                    if uid_dict2:
                        paipu2 = uid_dict2["paipu"]
                        uid2 = paipu2.split("_")[0]
                        task_id2 = self.motrol.get_taskport(token[1]['token'], token[1]['agent'], token[1]['cookie'], paipu2)
                        if task_id2:
                            logger.info(f"uid2：{uid2}")
                            token[1]['paipu'] = paipu2
                            token[1]['task_id'] = task_id2
                            token[1]['result_key'] = uid_dict2["result_key"]
                            await self.redis.push("get_json", token[1])
                        else:
                            await self.redis.push_before("get_token_result", uid_dict2)
        finally:
            await context.close()
            if hasattr(myChrome, "playwright"):
                await myChrome.playwright.stop()
            async with self.lock:
                self.running_dirs.remove(user_name)
                self.active_workers -= 1


async def chrome_get_token_main():
    aredis = AsyncRedisTool(db=8)
    await aredis.connect()
    api = TokenService(aredis=aredis, count=2)
    # 从redis获取任务，大概率任务是不会出现重复的
    asyncio.create_task(api._worker())
    # 主协程只需要等待，不阻塞事件循环
    try:
        while True:
            await asyncio.sleep(1)  # 或者 其他时间间隔
    except KeyboardInterrupt:
        logger.info("服务关闭中...")


if __name__ == "__main__":
    asyncio.run(chrome_get_token_main())
