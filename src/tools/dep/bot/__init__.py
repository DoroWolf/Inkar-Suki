'''
机器人相关组件
'''
import sys
import os
from sgtpyutils.logger import logger
try:
    logger.debug(f'load dependence:{__name__}')
except:
    pass

'''初始化基础环境'''
from .bot_env import *

'''初始化nonebot'''
from nonebot import on, on_command, require, on_message, on_regex
from nonebot import get_driver
from nonebot.adapters.onebot.v11 import Event, MessageSegment as ms
from nonebot.adapters import Message, MessageSegment
from nonebot.params import CommandArg, Arg
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message as obMessage
from nonebot.adapters.onebot.v11.message import Message as v11Message
from nonebot.adapters.onebot.v11.event import Anonymous, Sender, Reply
from nonebot.typing import T_State
from tabulate import tabulate
from pathlib import Path
from nonebot.message import handle_event
from nonebot import get_bots
matcher_common_run = on_message(priority=3, block=False)
import nonebot
tools_path = f"{os.getcwd()}/src/tools"
nonebot.init(tools_path=tools_path, log_level="INFO")


'''初始调用库'''
from sgtpyutils.database import filebase_database
from ...file import *
try:
    # 子依赖应后加载
    from .path import *
    from .bot_plugins import *
    from src.tools.permission import checker as permission_check, error as permission_error, permission_judge, Permission, PermissionResult
except:
    pass
