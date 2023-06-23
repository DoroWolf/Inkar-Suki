from src.tools.dep import *

async def news_():
    full_link = "https://www.jx3api.com/data/web/news?limit=5"
    info = await get_api(full_link, proxy = proxies)
    def dtut(date, title, url, type_):
        return f"{date}{type_}：{title}\n{url}"
    msg = ""
    for i in info["data"]:
        msg = msg + dtut(i["date"], i["title"], i["url"], i["type"]) + "\n"
    return msg