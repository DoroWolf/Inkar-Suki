from sgtpyutils.datetime import DateTime
import re


def get_number(number):
    '''
    返回参数的数值，默认返回0
    '''
    if not checknumber(number):
        return 0
    return int(number)


def checknumber(value):
    '''
    检查参数是否是数值
    '''
    if value is None:
        return False
    if isinstance(value, str):
        pattern = r'^[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$'
        return bool(re.match(pattern, value))
    if isinstance(value, int):
        return True
    return value.isdecimal()


def convert_time(timestamp: int, format: str = '%Y年%m月%d日 %H:%M:%S'):
    '''
    时间转换，自适应时间长度。
    '''
    return DateTime(timestamp).tostring(format)


def nodetemp(nickname: str, qqnumber: str, message: str) -> dict:
    return {"type": "node", "data": {"name": nickname, "uin": qqnumber, "content": message}}


def prefix(event, prefix):
    if str(event.raw_message)[0] != prefix:
        return False
    return True
