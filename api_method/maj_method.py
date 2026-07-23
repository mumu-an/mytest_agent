import requests
import time
import urllib.parse
import copy
from pathlib import Path
from urllib.parse import urlparse, parse_qs

class AmaeKoromo:
    def __init__(self):
        self.headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'origin': 'https://amae-koromo.sapk.ch',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'sec-ch-ua': '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36'
        }

    def get_historydata(self, player_id=8685617, timestamp=None, limit=100, mode=".".join(["12"]), paipu_uuid=None):
        """
        查询牌谱屋指定段位场的条件数据
        :param player_id: 玩家ID
        :param timestamp: 结束时间戳
        :param limit: 查询的数量
        :param mode: 查询的段位场，金东8，金9，玉12，玉东11，王16，格式".".join(["8","9","12"])
        :return: 返回历史对局的数据ID，顺序是旧到新，方便做表统计
        """
        if timestamp is None:
            timestamp = int(time.time() * 1000)
        result = {}

        while limit > 0:
            page_limit = min(limit, 500)
            url = f"https://5-data.amae-koromo.com/api/v2/pl4/player_records/{player_id}/{timestamp}/1262304000000?limit={page_limit}&mode={mode}&descending=true&tag="
            response = requests.request("GET", url, headers=self.headers)
            rpj = response.json()

            if not rpj:
                break

            # 找到指定牌谱就直接返回
            if paipu_uuid:
                uuids_dict = {item.get('uuid'): [player.get('gradingScore') for player in item.get('players', []) if player.get('accountId') == player_id] for item in rpj if item.get('uuid')}
                if paipu_uuid in uuids_dict.keys():
                    grading_score = uuids_dict[paipu_uuid][0]
                    return {
                        paipu_uuid: {
                            "score": grading_score
                        }
                    }
            else:
                for item in reversed(rpj):
                    uuid = item.get('uuid')

                    if not uuid:
                        continue

                    grading_score = None

                    for player in item.get('players', []):
                        if player.get('accountId') == player_id:
                            grading_score = player.get('gradingScore')
                            break

                    result[uuid] = {"score": grading_score}

                limit -= len(rpj)

                # 下一页时间戳
                timestamp = rpj[-1].get('startTime') * 1000 - 1

                # 不足一页说明没数据了
                if len(rpj) < page_limit:
                    break

        return result if result else None

    def search_player_id(self, player_name="小诗乃"):
        """
        查询指定昵称的牌谱屋ID
        :param player_name: 查询昵称
        :return:
        """
        url = f"https://5-data.amae-koromo.com/api/v2/pl4/search_player/{urllib.parse.quote(player_name)}?limit=20&tag=all"
        response = requests.request("GET", url, headers=self.headers)
        rpj = response.json()
        if not rpj:
            return None
        else:
            for player in rpj:
                if player['nickname'] == player_name:
                    return player['id']
            return None

    def search_player_msg(self, player_id=8685617, mode=".".join(["12"])):
        """
        返回玩家指定段位场的场次数量
        :param player_id: 玩家ID
        :param mode: 查询的段位场，金东8，金9，玉12，玉东11，王16，格式".".join(["8","9","12"])
        :return:
        """
        url = f"https://5-data.amae-koromo.com/api/v2/pl4/player_stats/{player_id}/1262304000000/1779090659999?mode={mode}&tag={int(time.time() // 3600)}"
        response = requests.request("GET", url, headers=self.headers)
        rpj = response.json()
        if not rpj:
            return None
        else:
            return rpj['count']

    @staticmethod
    def get_motroplayid(player_id=8685617):
        """
        查询指定牌谱的玩家的motrol ID
        :param player_id: 牌谱屋ID
        :return:
        """
        return 1358437 + ((7 * player_id + 1117113) ^ 86216345)

    @staticmethod
    def get_player_id(motrol_id: int = 111674862) -> int:
        return (((motrol_id - 1358437) ^ 86216345) - 1117113) // 7

class Motrol:
    def __init__(self):
        self.taskportheaders = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://mjai.ekyu.moe',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
        }
        self.ratingheaders = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
        }

        self.getjsonheaders = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'upgrade-insecure-requests': '1',
        }

    def get_taskport(self, token, agent, cookie, paipu):
        url = "https://mjai.ekyu.moe/review"
        payload = {
            "input-method": "log-url",
            "log-url": f"https://game.maj-soul.com/1/?paipu={paipu}",
            "riichi-city-log-id": "",
            "hime-mahjong-region": "china",
            "hime-mahjong-log-id": "",
            "tenhou6": "",
            "player-id": "",
            "engine": "mortal",
            "mortal-model-tag": "4.1b",
            "ui": "killerducky",
            "lang": "zh-CN",
            "temperature": "",
            "kyokus": "",
            "cf-turnstile-response": token
        }
        headers = copy.deepcopy(self.taskportheaders)
        headers['user-agent'] = agent
        headers['Cookie'] = cookie
        response = requests.request("POST", url, headers=headers, data=payload)
        query = parse_qs(urlparse(response.url).query)
        task_id = query.get("task", [None])[0]
        if not task_id:
            data = query.get("data", [None])[0]

            if data and "/report/" in data:
                task_id = Path(data).stem
        return task_id

    def get_rating(self, agent, cookie, task_id):
        try:
            headers = copy.deepcopy(self.ratingheaders)
            headers['user-agent'] = agent
            headers['Cookie'] = cookie
            headers['referer'] = f"https://mjai.ekyu.moe/killerducky/?data=/report/{task_id}.json"
            url = f"https://mjai.ekyu.moe/report/{task_id}.json"
            response = requests.request("GET", url, headers=headers)
            # print(response.status_code)
            if response.status_code == 200:
                rpj = response.json()
                return round(rpj['review']['rating'] * 100, 2)
            elif response.status_code == 404:
                return None
        except:
            return None

if __name__ == "__main__":
    print(AmaeKoromo().get_historydata(limit=2))

