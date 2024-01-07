from src.tools.dep import *
from .help_document import *
from src.tools.local_version import nbv
from nonebot.adapters.onebot.v11 import unescape
import psutil


purge = on_command("purge", priority=5)  # 清除所有`help`生成的缓存图片


@purge.handle()
async def ___(event: Event):
    x = Permission(event.user_id).judge(1, '清除缓存')
    if not x.success:
        return await purge.finish(x.description)
    try:
        for i in os.listdir(bot_path.CACHE):
            os.remove(bot_path.CACHE + "/" + i)
    except Exception as _:
        return await purge.finish("部分文件并没有找到哦~")
    else:
        return await purge.finish("好的，已帮你清除图片缓存~")

shutdown = on_command("shutdown", aliases={"poweroff"}, priority=5)  # 关掉`Inkar-Suki`主程序


@shutdown.handle()
async def ____(event: Event):

    x = Permission(event.user_id).judge(10, '关闭机器人')
    if not x.success:
        return await shutdown.finish(x.description)
    await shutdown.send("请稍候，正在关闭中……")
    await shutdown.send("关闭成功！请联系Owner到后台手动开启哦~")
    sys.exit(0)

restart = on_command("restart", priority=5)  # 重启`Inkar-Suki`，原理为`FastAPI`的文件监控自动重启


@restart.handle()
async def _(event: Event):
    with open("./src/plugins/developer_tools/example.py", mode="w") as cache:
        x = Permission(event.user_id).judge(5, '重启机器人')
        if not x.success:
            return await restart.finish(x.description)
        await restart.send("好啦，开始重启，整个过程需要些许时间，还请等我一下哦~")
        cache.write("status=\"OK\"")

echo = on_command("echo", priority=5)  # 复读只因功能


@echo.handle()
async def echo_(event: Event, args: v11Message = CommandArg()):
    x = Permission(event.user_id).judge(9, '复读说话')
    if not x.success:
        return await echo.finish(x.description)
    return await echo.finish(args)

say = on_command("say", priority=5)  # 复读只因 + CQ码转换（mix：没有CQ码）


@say.handle()
async def say_(event: Event, args: v11Message = CommandArg()):
    def _unescape(message: v11Message, segment: MessageSegment):
        if segment.is_text():
            raw = unescape(str(segment))
            return message.append(raw)
        return message.append(segment)

    x = Permission(event.user_id).judge(10, '高级复读说话')
    if not x.success:
        return await say.finish(x.description)
    message = extensions.reduce(args, _unescape, v11Message())
    return await say.finish(message)

ping = on_command("ping", aliases={"-测试"}, priority=5)  # 测试机器人是否在线


@ping.handle()
async def _(event: Event):
    x = Permission(event.user_id).judge(1, '运行状态详细')
    if not x.success:
        times = str("现在是"
                    + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    + f"\nNonebot {nbv}")
        return await ping.finish(times)

    def per_cpu_status() -> List[float]:
        return psutil.cpu_percent(interval=1, percpu=True)

    def memory_status() -> float:
        return psutil.virtual_memory().percent
    times = str("现在是"
                + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                + f"\nNonebot {nbv}"
                )
    msg = f"来啦！\n\系统信息如下：\nCPU占用：{str(per_cpu_status()[0])}%\n内存占用：{str(memory_status())}%\n"
    return await ping.finish(msg + times)

post = on_command("post", priority=5)  # 发送全域公告至每一个机器人加入的QQ群。


@post.handle()
async def _(bot: Bot, event: Event, args: v11Message = CommandArg()):
    if str(event.user_id) not in Config.owner:
        return await post.finish("唔……只有机器人主人可以使用该命令哦~")
    cmd = args.extract_plain_text()
    groups = await bot.call_api("get_group_list")
    for i in groups:
        await bot.call_api("send_group_msg",
                           group_id=i["group_id"],
                           message=cmd
                           )

call_api = on_command("call_api", aliases={"api"}, priority=5)  # 调用`go-cqhttp`的`API`接口。


@call_api.handle()
async def _(event: Event, args: v11Message = CommandArg()):
    x = Permission(event.user_id).judge(10, '调用nb-api')
    if not x.success:
        return await call_api.finish(x.description)
    cmd = args.extract_plain_text()
    result = await get_url(f"{Config.cqhttp}{cmd}")
    return call_api.send(f'已执行{cmd} -> {result}')

git = on_command("-git", priority=5)  # 调用`Git`，~~别问意义是什么~~


@git.handle()
async def _(event: Event, args: v11Message = CommandArg()):
    x = Permission(event.user_id).judge(10, '调用git')
    if not x.success:
        return await call_api.finish(x.description)
    output = ""
    commit = args.extract_plain_text()
    if commit == "pull":
        output = os.popen("git pull").read()
        return await git.finish(output)
    os.system("git add .")
    msg = ""
    msg = msg + os.popen("git commit -m \""
                         + commit
                         + "\""
                         ).read()
    msg = msg + os.popen("git push").read()
    if msg == "":
        msg = "执行完成，但没有输出哦~"
    return await git.finish(msg)

voice = on_command("voice", priority=5)  # 调用腾讯的语音TTS接口，生成语音。


@voice.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: v11Message = CommandArg()):

    x = Permission(event.user_id).judge(10, '调用nb-api')
    if not x.success:
        return await call_api.finish(x.description)
    sth = args.extract_plain_text()
    final_msg = f"[CQ:tts,text={sth}]"
    await bot.call_api("send_group_msg",
                       group_id=event.group_id,
                       message=final_msg
                       )

util_cmd_web = on_command(
    "util_web",
    name="网页截图",
    aliases={"web"},
    priority=5,
    description='网页截图，需要网址',
    catalog=permission.jx3.pvx.property.horse.chitu,
    example=[
        Jx3Arg(Jx3ArgsType.url)
    ],
    document='''通过截图'''
)


@util_cmd_web.handle()
async def util_web(bot: Bot, event: GroupMessageEvent, args: list[Any] = Depends(Jx3Arg.arg_factory)):
    x = Permission(event.user_id).judge(10, '调用网页截图')
    if not x.success:
        return await util_cmd_web.finish(x.description)

    url, = args
    image = await generate_by_url(url, delay=1000)
    img = ms.image(Path(image).as_uri())
    return await util_cmd_web.send(v11Message(f'{img}\n网页截图完成'))

apply = on_command(
    "apply",
    aliases={
        "申请", "领养", "购买", f"要一个{bot}",
        f"想要一个{bot}", f"想有一个{bot}", f"{bot}", '机器人',
    },
    priority=5,
    description='获取如何拉机器人入群',
    catalog=permission.mgr.group.apply,
    example=[],
    document=''''''
)


@apply.handle()
async def _(state: T_State, event: Event):
    applier = str(event.user_id)
    state["user"] = applier
    steps = [
        '加我为好友，答案:sin y',
        '加用户群650495414',
        '拉我进想要的群',
        '拉完找管理说一声',
        '等管理同意申请'
    ]
    steps = [f'{index+1}.{x}' for (index, x) in enumerate(steps)]
    steps = str.join('\n', steps)
    return await apply.finish(f'是要领养{bot}吗，免费的：\n{steps}')


# @apply.got("group", prompt="感谢您申请使用Inkar Suki，接下来请发送您所为之申请的群聊的群号。")
async def _(bot: Bot, state: T_State, group: v11Message = Arg()):
    group_id = group.extract_plain_text()
    if checknumber(group_id) is False:
        return await apply.finish("输入的内容有误，申请失败。")
    else:
        try:
            data = json.dumps(await bot.call_api("get_group_info", group_id=int(group_id)), ensure_ascii=False)
        except Exception as _:
            data = "获取失败！"
        if data == "获取失败！":
            return await apply.finish("您的申请没有成功，抱歉！\n请检查该群是否能被搜索到。")
        repo_name = Config.repo_name
        url = f"https://api.github.com/repos/{repo_name}/issues"
        token = Config.ght
        user = state["user"]
        bearer = "Bearer " + token
        final_header = {
            "Accept": "application/vnd.github+json",
            "Authorization": bearer,
            "X-GitHub-Api-Version": "2022-11-28"}
        body = {
            "title": "Inkar-Suki·使用申请",
            "body": f"申请人QQ：{user}\n申请群聊：{group_id}\n群聊请求数据如下：```{data}```",
            "labels": ["申请"]
        }
        resp = await data_post(
            url,
            headers=final_header,
            json=body
        )
        logger.info(resp)
        return await apply.finish("申请成功，请求已发送至GitHub，请等待通知！")
