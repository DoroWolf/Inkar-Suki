from src.tools.file import read
import json
from src.tools.utils import *
from pathlib import Path


def judge(qqnumber):
    file = open(bot_path.TOOLS+"/permission.json", mode="r")
    json_ = json.loads(file.read())
    file.close()
    if qqnumber not in json_:
        return False
    else:
        return True


class PermissionResult:
    success: bool
    user_level: int
    description: str

    def __init__(self, success: bool, user_level: int, description: str, required: any = None) -> None:
        self.success = success
        self.user_level = user_level
        self.description = description
        self.required = required

    def __str__(self) -> str:
        status = '授权' if self.success else '拒绝访问'
        x = f'{status}:{self.description},u_level:{self.user_level}'
        if self.required:
            x = f'{x}{self.required}'
        return x

    def __repr__(self) -> str:
        return self.__str__()


class Permission:
    # TODO 使用sql
    # TODO 记录授权日志
    # TODO 按permission.types功能点授权
    # TODO use AOP to auto-reply by judgement.
    def __init__(self, user_id: str) -> None:
        self.user_id = str(user_id)
        self.u_level = self.init_permission()

    def init_permission(self) -> int:
        file = read(bot_path.TOOLS+"/permission.json")
        self.permissions = json.loads(file)
        if self.user_id not in self.permissions:
            return None
        return int(self.permissions[self.user_id])

    @ext.use_log()
    def judge(self, score: int, action: str = '该操作') -> PermissionResult:
        if not isinstance(score, int):
            score = int(score)
        u_level = self.u_level
        prefix = f'唔……{action}需要授权,但你'
        if u_level is None:
            return PermissionResult(False, None, f'{prefix}没有任何授权哦~')
        if u_level < score:
            return PermissionResult(False, u_level, f'{prefix}的权限只有{u_level}级，要求{score}级~')
        return PermissionResult(True, u_level, None)


def checker(qqnumber: str, score: int) -> bool:
    x = Permission(qqnumber).judge(score)
    return x.success


def permission_judge(qqnumber: str, score: int, action: str = '该操作') -> tuple[bool, int, str]:
    x = Permission(qqnumber).judge(score, action)
    return (x.success, x.user_level, x.description)


def error(score):
    return f"唔……你权限不够哦，这条命令要至少{score}的权限哦~"


def block(sb: str) -> bool:
    with open(bot_path.TOOLS+"/ban.json", mode="r") as cache:
        for i in json.loads(cache.read()):
            if i == sb:
                return True
        return False
