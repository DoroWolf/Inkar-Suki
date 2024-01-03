from __future__ import annotations
import httpx
import time

from bs4 import BeautifulSoup, element
from httpx import Response as XResponse

from src.tools.dep import *
from src.tools.generate import get_uuid


class Response:
    def __init__(self, data: dict) -> None:
        if data is None:
            data = '{}'
        if isinstance(data, XResponse):
            data = data.json()
        if isinstance(data, str):
            data = json.loads(data)

        self.code = data.get("code")
        self._data = data.get("data")

    @property
    def success(self):
        return self.code == 1


class TipResponse(Response):
    def __init__(self, data: dict) -> None:
        super().__init__(data)
        if not self.success:
            self.results = None
            return
        self.items = self._data.get("items")
        if self.items is None:
            self.results = None
            return
        self.results = [x.get("content") for x in self.items]

    def to_dict(self):
        return {"results": self.results, "items": self.items}


class QuesResponseHandler:
    @staticmethod
    def txt_handler(x: dict):
        return x.get("answerContent")

    @staticmethod
    def confirm_ak_handler(x: dict):
        confirmList = x.get("confirmList")
        confirmListTxt = [x.get('matchQuestionString') for x in confirmList]
        confirmListTxt = [f'<p data-question="1">{x}</p>' for x in confirmListTxt]
        confirmListTxt = ['<p>尝试换个方式问问</p>', x.get('guideWords')] + confirmListTxt
        return f"<p>{str.join('', confirmListTxt)}</p>"

    @staticmethod
    def material_handler(x: dict):
        '''# TODO 超链接、图像、视频、音频、office文件等'''
        material = x.get('material')
        path = material.get('path')
        return f'<p><img src="{path}" style="width:100%" /></p>'


class QuesResponse(Response):
    msg_type_handler = {
        'MSG_TXT': QuesResponseHandler.txt_handler,
        'MSG_MATERIAL': QuesResponseHandler.material_handler,
        'MSG_CONFIRM_ASK': QuesResponseHandler.confirm_ak_handler,
    }

    def __init__(self, data: dict) -> None:
        super().__init__(data)
        # logger.debug(f"question response loaded(success:{self.success})")
        if not self.success:
            self.results = None
            return
        self.items = self._data.get("robotResults")
        # logger.debug(f"question response items:{self.items}")
        if self.items is None:
            self.results = None
            return

        def filter_content(x: dict):
            msg_type = x.get('resultFormatType')
            handler = QuesResponse.msg_type_handler.get(msg_type)
            if not handler:
                return f'[未知的消息类型:{msg_type}，请联系管理员]'
            return handler(x)

        self.results = [filter_content(x) for x in self.items]
        # 当没有回答时返回该列表
        self.confirm_list = [x.get("confirmList") for x in self.items]
        self.relateds = []  # 相关问题

    def to_dict(self):
        return {
            "results": self.results,
            "items": self.items,
            "relateds": self.relateds,
            "confirm_list": self.confirm_list
        }


class Jx3GuidResult:
    tip: TipResponse = None
    question: QuesResponse = None

    def __init__(self, tip: TipResponse, ques: QuesResponse) -> None:
        self.tip = tip
        self.question = ques

    def to_dict(self):
        return {"tip": self.tip.to_dict(), "question": self.question.to_dict()}


class Jx3Guide:
    API_web_host = "https://chatrobot.xoyo.com/"
    API_host = f"{API_web_host}chatbot/"
    # 初始化
    API_init = "web/init/{channel}?sysNum={channel}&sourceId={source}&lang=zh_CN&_={timestamp}"
    # 获取提示
    API_tip = "web/inputPrompt/{channel}?sourceId={source}&question={question}&_={timestamp}"
    # 发送问题
    API_ques = "web/chat/{channel}?sourceId={source}"

    CHANNEL_Init = "1578898069071"
    CHANNEL_TIP = "1578898069072"

    def with_headers(self, raw: dict = None):
        if raw is None:
            raw = {}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }
        headers.update(raw)
        return headers

    def __init__(self, question: str) -> None:
        self.question = question
        self.session = httpx.AsyncClient(headers=self.with_headers())

    @staticmethod
    def get_url(url: str) -> str:
        u = url.replace("{timestamp}", str(int(time.time() * 1e3)))
        u = u.replace("{source}", "62203")
        u = f"{Jx3Guide.API_host}{u}"
        return u

    async def _step_init(self):
        url = Jx3Guide.get_url(Jx3Guide.API_init)
        url = url.replace("{channel}", Jx3Guide.CHANNEL_Init)
        data = await get_api(url, client=self.session)
        r = Response(data)
        return r

    async def _step_get_tip(self):
        url = Jx3Guide.get_url(Jx3Guide.API_tip)
        url = url.replace("{channel}", Jx3Guide.CHANNEL_Init)
        url = url.replace("{question}", self.question)
        data = await get_api(url, client=self.session)
        res = TipResponse(data)

        return res

    async def _step_ques(self):
        url = Jx3Guide.get_url(Jx3Guide.API_ques)
        url = url.replace("{channel}", Jx3Guide.CHANNEL_Init)
        payload = {"content": self.question, "type": 0, "x": 0, "y": 0}
        headers = {
            "Content-Type": "application/json"
        }
        # logger.debug(f"wiki question set:{self.question}")
        data = await post_url(url, json=payload, headers=self.with_headers(headers), client=self.session)
        res = QuesResponse(data)
        await self.handle_answer(res)
        return res

    async def handle_single_res(self, res: str):
        if not res:
            return
        doc = BeautifulSoup(res)
        ##############处理图片#################
        imgs = doc.find_all("img")
        for img in imgs:
            img: element.Tag = img
            src = img.attrs.get("src")
            if not src:
                continue
            if not src.startswith(Jx3Guide.API_web_host):
                src = f"{Jx3Guide.API_web_host}{src}"
            img_data = await send_with_async('get', src, client=self.session)
            if not img_data.status_code == 200:
                img.attrs["src"] = ""  # 错误
                continue
            img_data = img_data.content
            uuid = get_uuid()
            img_file = f"{CACHE}{os.sep}{uuid}.png"
            with open(img_file, "wb") as f:
                f.write(img_data)
            img.attrs["src"] = Path(img_file).as_uri()
        ##############处理图片#################

        ##############处理段落#################
        paras = doc.find_all("p")
        result = []
        relateds = []
        for p in paras:
            contents = p.contents
            r = []
            for index in range(len(contents)):
                data = contents[index]
                if not type(data) == element.Tag:
                    r.append(data.get_text())
                    continue  # 非标签则直接添加文字
                if data.has_attr("src"):
                    r.append(["IMG", data.attrs.get("src")])
                    continue  # 图片
                if data.has_attr("data-question"):
                    related_ques = data.attrs.get("data-question")
                    x = ["RELA", related_ques]
                    relateds.append(related_ques)
                    r.append(x)  # 关联问题
                r.append(data.get_text())
            result.append([x for x in r if x])  # 加入并排除空数据
        ##############处理段落#################
        return [result, relateds]

    async def handle_answer(self, res: QuesResponse):
        r = [await self.handle_single_res(x) for x in res.results if x]
        res.results = [[x for x in paras[0] if x] for paras in r if paras]
        res.relateds = extensions.flat(
            [[x for x in paras[1] if x] for paras in r if paras])
        # logger.debug(f"answers handled:{res.results},{res.relateds}")

        if not res.results:
            res.results = [['没有找到这个问题的答案，尝试换个方式问问']]

    async def run_async(self):
        await self._step_init()
        tips = await self._step_get_tip()
        result = await self._step_ques()
        return Jx3GuidResult(tips, result)


async def get_guide(submit: str) -> Jx3GuidResult:
    """
    获取jx3萌新指引的截图
    """
    r = await Jx3Guide(submit).run_async()
    # logger.debug(f"guide completed:{r.to_dict()}")
    return r

if __name__ == "__main__":
    asyncio.run(get_guide("五行石"))
