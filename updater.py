try:
    from selectolax.parser import HTMLParser
    import orjson
    from curl_cffi import requests
except (ModuleNotFoundError, ImportError):
    print("Hint: Try doing \"pip install -r requirements.txt\"")
    import sys
    sys.exit()

import random
from typing import NamedTuple, Optional


default_frauds =  [
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.3",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.3",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.3",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) GSA/323.0.647062479 Mobile/15E148 Safari/604.",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.2 Mobile/15E148 Safari/604.",
    "Mozilla/5.0 (Android 13; Mobile; rv:127.0) Gecko/127.0 Firefox/127.",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/24.0 Chrome/117.0.0.0 Mobile Safari/537.3",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/126.0.6478.153 Mobile/15E148 Safari/604.",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) GSA/277.0.555192628 Mobile/15E148 Safari/604.",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Mobile/15E148 Safari/604.",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.136 Mobile Safari/537.36 XiaoMi/MiuiBrowser/14.13.0-g",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_7_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Mobile/15E148 Safari/604.",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/25.0 Chrome/121.0.0.0 Mobile Safari/537.3",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.3",
    "Mozilla/5.0 (Linux; Android 10; MED-LX9N; HMSCore 6.13.0.351) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.88 HuaweiBrowser/14.0.5.302 Mobile Safari/537.3",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Mobile/15E148 Safari/604.",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36 OPR/83.0.0.",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.",
]

def random_user_agent():
    return random.choice(default_frauds)


class UserAgents(NamedTuple):
    type:str
    agents:list[str]


def agents_from_dict(data: list[dict[str, str]]) -> set[str]:
    return {d["ua"] for d in data}

def parse_agents(html:bytes) -> dict[str, list[str]]:
    user_agents_dict = {}
    for d in HTMLParser(html).css("h3"):
        if d.text(strip=True) == "JSON":
            parent = d.parent
            name = parent.parent.attributes["id"].removesuffix("-useragents-json-csv").removeprefix("most-common-")
            data = orjson.loads(parent.css_first("textarea").text(strip=True))
            user_agents_dict[name] = list(agents_from_dict(data))
    return user_agents_dict

def request_user_agents(proxy:Optional[str] = None):
    response = requests.get("https://useragents.me", proxy=proxy, headers={"User-Agent": random_user_agent()})
    # ensure we don't get parsing errors later which would be very bad!
    response.raise_for_status()
    return response.content 

def scrape_user_agents(proxy:Optional[str] = None):
    return parse_agents(request_user_agents(proxy))

def write_json(data:dict[str, UserAgents]):
    with open("user-agents.json", "wb") as j: 
        j.write(orjson.dumps(data))


if __name__ == "__main__":
    write_json(scrape_user_agents())

