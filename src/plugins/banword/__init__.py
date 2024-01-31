from src.tools.dep import *
from src.tools.file import read, write
from src.tools.permission import checker, error
import json
import sys
import nonebot

from nonebot.adapters.onebot.v11 import MessageSegment as ms
from nonebot import on_command
from nonebot import on_message
from nonebot.adapters import Message
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.params import CommandArg

global flag

banword = on_command("banword", priority=5)


@banword.handle()
async def __(event: GroupMessageEvent, args: Message = CommandArg()):  # 违禁词封锁
    bw = args.extract_plain_text()
    if checker(str(event.user_id), 5) == False:
        await banword.finish(error(5))
    if bw:
        now = json.loads(read(bot_path.DATA + "/" + str(event.group_id) + "/banword.json"))
        if bw in now:
            return await banword.finish("唔……封禁失败，已经封禁过了。")
        now.append(bw)
        write(bot_path.DATA + "/" + str(event.group_id) + "/banword.json", json.dumps(now, ensure_ascii=False))
        return await banword.finish("已成功封禁词语！")
    else:
        return await banword.finish("您封禁了什么？")

unbanword = on_command("unbanword", priority=5)  # 违禁词解封


@unbanword.handle()
async def ___(event: GroupMessageEvent, args: Message = CommandArg()):
    if checker(str(event.user_id), 5) == False:
        await unbanword.finish(error(5))
    cmd = args.extract_plain_text()
    if cmd:
        now = json.loads(read(bot_path.DATA + "/" + str(event.group_id) + "/banword.json"))
        try:
            now.remove(cmd)
            write(bot_path.DATA + "/" + str(event.group_id) + "/banword.json",
                  json.dumps(now, ensure_ascii=False))
            return await unbanword.finish("成功解封词语！")
        except ValueError:
            return await unbanword.finish("您解封了什么？")
    else:
        return await unbanword.finish("您解封了什么？")

@matcher_common_run.handle()
async def _(matcher: Matcher, bot: Bot, event: GroupMessageEvent):
    if checker(str(event.user_id),5):
        return
    flag = False
    banwordlist = json.loads(read(bot_path.DATA + "/" + str(event.group_id) + "/banword.json"))
    msg = event.get_plaintext()
    id_ = str(event.message_id)
    for i in banwordlist:
        if msg.find(i) != -1:
            flag = True
    if flag:
        sb = event.user_id
        try:
            group = event.group_id
            await bot.call_api("delete_msg", message_id = id_)
            await bot.call_api("set_group_ban", group_id = group, user_id = sb, duration = 60)
            msg = ms.at(sb) + "唔……你触发了违禁词，已经给你喝了1分钟的红茶哦~"
            matcher.stop_propagation()
            await matcher_common_run.finish(msg)
        except:
            pass
    else:
        pass