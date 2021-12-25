#edited by HeLLxGodLike all credits goes to team DaisyX

import re
import requests
import emoji

url = "https://acobot-brainshop-ai-v1.p.rapidapi.com/get"
import re

import aiohttp
from googletrans import Translator as google_translator
# from google_trans_new import google_translator
from pyrogram import filters
from SungJinwooRobot import arq
from SungJinwooRobot.utils.aichat import add_chat, get_session, remove_chat
from SungJinwooRobot.utils.pluginshelper import admins_only, edit_or_reply
from SungJinwooRobot import pgram as daisyx

translator = google_translator()

BOT_ID = 1485865042

async def lunaQuery(query: str, user_id: int):
    luna = await arq.luna(query, user_id)
    return luna.result


def extract_emojis(s):
    return "".join(c for c in s if c in emoji.UNICODE_EMOJI)


async def fetch(url):
    try:
        async with aiohttp.Timeout(10.0):
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    try:
                        data = await resp.json()
                    except:
                        data = await resp.text()
            return data
    except:
        print("AI response Timeout")
        return


daisy_chats = []
en_chats = []
# AI Chat (C) 2020-2021 by @InukaAsith


@daisyx.on_message(
    filters.command("chatbot") & ~filters.edited & ~filters.bot & ~filters.private
)
@admins_only
async def hmm(_, message):
    global daisy_chats
    if len(message.command) != 2:
        await message.reply_text(
            "I only recognize `/chatbot on` and /chatbot `off only`"
        )
        message.continue_propagation()
    status = message.text.split(None, 1)[1]
    chat_id = message.chat.id
    if status == "ON" or status == "on" or status == "On":
        lel = await edit_or_reply(message, "`Processing...`")
        lol = add_chat(int(message.chat.id))
        if not lol:
            await lel.edit("Sung Jinwoo AI Already Activated In This Chat")
            return
        await lel.edit(
            f"Sung Jinwoo AI Successfully Added For Users In The Chat"
        )

    elif status == "OFF" or status == "off" or status == "Off":
        lel = await edit_or_reply(message, "`Processing...`")
        Escobar = remove_chat(int(message.chat.id))
        if not Escobar:
            await lel.edit("SUNG AI Was Not Activated In This Chat")
            return
        await lel.edit(
            f"Sung Jinwoo AI Successfully Deactivated For Users In The Chat"
        )

    elif status == "EN" or status == "en" or status == "english":
        if not chat_id in en_chats:
            en_chats.append(chat_id)
            await message.reply_text("English AI chat Enabled!")
            return
        await message.reply_text("AI Chat Is Already Disabled.")
        message.continue_propagation()
    else:
        await message.reply_text(
            "I only recognize `/chatbot on` and /chatbot `off only`"
        )


@daisyx.on_message(
    filters.text
    & filters.reply
    & ~filters.bot
    & ~filters.edited
    & ~filters.via_bot
    & ~filters.forwarded,
    group=2,
)
async def hmm(client, message):
    if not get_session(int(message.chat.id)):
        return
    if not message.reply_to_message:
        return
    try:
        senderr = message.reply_to_message.from_user.id
    except:
        return
    if senderr != BOT_ID:
        return
    msg = message.text
    chat_id = message.chat.id
    if msg.startswith("/") or msg.startswith("@"):
        message.continue_propagation()
    if chat_id in en_chats:
        test = msg
        test = test.replace("Sung", "Aco")
        test = test.replace("Sung", "Aco")
        test = test.replace("I was created by @The_Pirate_Hunter", "I made myself")
        test = test.replace("Hello there I am SungJinWoo...nice to meet u", "Hi, my friend! Do you want me to tell you a joke?")
        test = test.replace("@The_Pirate_Huntee is my owner" , "Have the control right.")
        test = test.replace("Hi, My name is SungJinWoo Nice to meet you." , "Hi, my friend, what can I do for you today?")
       
        response = await lunaQuery(
            test, message.from_user.id if message.from_user else 0
        )
        response = response.replace("Aco", "Sung")
        response = response.replace("aco", "Sung")
        response = response.replace("I made myself", "I was Created by @The_Pirate_Hunter")
        response = response.replace("Hi, my friend! Do you want me to tell you a joke?", "Hello there I am SungJinWoo...nice to meet u")
        response = response.replace("Have the control right." , "@The_Pirate_Hunter is my owner.")
        response = response.replace("Hi, my friend, what can I do for you today?" , "Hi, My name is SungJinWoo Nice to meet you")
        pro = response
        try:
            await daisyx.send_chat_action(message.chat.id, "typing")
            await message.reply_text(pro)
        except CFError:
            return

    else:
        u = msg.split()
        emj = extract_emojis(msg)
        msg = msg.replace(emj, "")
        if (
            [(k) for k in u if k.startswith("@")]
            and [(k) for k in u if k.startswith("#")]
            and [(k) for k in u if k.startswith("/")]
            and re.findall(r"\[([^]]+)]\(\s*([^)]+)\s*\)", msg) != []
        ):

            h = " ".join(filter(lambda x: x[0] != "@", u))
            km = re.sub(r"\[([^]]+)]\(\s*([^)]+)\s*\)", r"", h)
            tm = km.split()
            jm = " ".join(filter(lambda x: x[0] != "#", tm))
            hm = jm.split()
            rm = " ".join(filter(lambda x: x[0] != "/", hm))
        elif [(k) for k in u if k.startswith("@")]:

            rm = " ".join(filter(lambda x: x[0] != "@", u))
        elif [(k) for k in u if k.startswith("#")]:
            rm = " ".join(filter(lambda x: x[0] != "#", u))
        elif [(k) for k in u if k.startswith("/")]:
            rm = " ".join(filter(lambda x: x[0] != "/", u))
        elif re.findall(r"\[([^]]+)]\(\s*([^)]+)\s*\)", msg) != []:
            rm = re.sub(r"\[([^]]+)]\(\s*([^)]+)\s*\)", r"", msg)
        else:
            rm = msg
            # print (rm)
        try:
            lan = translator.detect(rm)
            lan = lan.lang
        except:
            return
        test = rm
        if not "en" in lan and not lan == "":
            try:
                test = translator.translate(test, dest="en")
                test = test.text
            except:
                return
        # test = emoji.demojize(test.strip())

        test = test.replace("Sung", "Aco")
        test = test.replace("Sung", "Aco")
        test = test.replace("I was created by @The_Pirate_Hunter", "I made myself")
        test = test.replace("Hello there I am SungJinWoo...nice to meet u", "Hi, my friend! Do you want me to tell you a joke?")
        test = test.replace("@The_Pirate_Hunter is my owner" , "Have the control right.")
        test = test.replace("Hi, My name is SungJinWoo Nice to meet you." , "Hi, my friend, what can I do for you today?")
        response = await lunaQuery(
            test, message.from_user.id if message.from_user else 0
        )
        response = response.replace("Aco", "Sung")
        response = response.replace("aco", "Sung")
        response = response.replace("Luna", "Sung")
        response = response.replace("luna", "Sung")
        response = response.replace("I made myself", "I was Created by @The_Pirate_Hunter")
        response = response.replace("Hi, my friend! Do you want me to tell you a joke?", "Hello there I am SungJinWoo...nice to meet u")
        response = response.replace("Have the control right." , "@The_Pirate_Hunter is my owner.")
        response = response.replace("Hi, my friend, what can I do for you today?" , "Hi, My name is SungJinWoo Nice to meet you")
        pro = response
        if not "en" in lan and not lan == "":
            try:
                pro = translator.translate(pro, dest=lan)
                pro = pro.text
            except:
                return
        try:
            await daisyx.send_chat_action(message.chat.id, "typing")
            await message.reply_text(pro)
        except CFError:
            return


@daisyx.on_message(
    filters.text & filters.private & ~filters.edited & filters.reply & ~filters.bot
)
async def inuka(client, message):
    msg = message.text
    if msg.startswith("/") or msg.startswith("@"):
        message.continue_propagation()
    u = msg.split()
    emj = extract_emojis(msg)
    msg = msg.replace(emj, "")
    if (
        [(k) for k in u if k.startswith("@")]
        and [(k) for k in u if k.startswith("#")]
        and [(k) for k in u if k.startswith("/")]
        and re.findall(r"\[([^]]+)]\(\s*([^)]+)\s*\)", msg) != []
    ):

        h = " ".join(filter(lambda x: x[0] != "@", u))
        km = re.sub(r"\[([^]]+)]\(\s*([^)]+)\s*\)", r"", h)
        tm = km.split()
        jm = " ".join(filter(lambda x: x[0] != "#", tm))
        hm = jm.split()
        rm = " ".join(filter(lambda x: x[0] != "/", hm))
    elif [(k) for k in u if k.startswith("@")]:

        rm = " ".join(filter(lambda x: x[0] != "@", u))
    elif [(k) for k in u if k.startswith("#")]:
        rm = " ".join(filter(lambda x: x[0] != "#", u))
    elif [(k) for k in u if k.startswith("/")]:
        rm = " ".join(filter(lambda x: x[0] != "/", u))
    elif re.findall(r"\[([^]]+)]\(\s*([^)]+)\s*\)", msg) != []:
        rm = re.sub(r"\[([^]]+)]\(\s*([^)]+)\s*\)", r"", msg)
    else:
        rm = msg
        # print (rm)
    try:
        lan = translator.detect(rm)
        lan = lan.lang
    except:
        return
    test = rm
    if not "en" in lan and not lan == "":
        try:
            test = translator.translate(test, dest="en")
            test = test.text
        except:
            return

    # test = emoji.demojize(test.strip())

    # Kang with the credits bitches @InukaASiTH
    test = test.replace("Sung", "Aco")
    test = test.replace("Sung", "Aco")
    test = test.replace("I was created by @The_Pirate_Hunter", "I made myself")
    test = test.replace("Hello there I am SungJinWoo...nice to meet u", "Hi, my friend! Do you want me to tell you a joke?")
    test = test.replace("@The_Pirate_Hunter is my owner" , "Have the control right.")
    test = test.replace("Hi, My name is SungJinWoo Nice to meet you." , "Hi, my friend, what can I do for you today?")

    response = await lunaQuery(test, message.from_user.id if message.from_user else 0)
    response = response.replace("Aco", "Sung")
    response = response.replace("aco", "Sung")
    response = response.replace("I made myself", "I was Created by @The_Pirate_Hunter")
    response = response.replace("Hi, my friend! Do you want me to tell you a joke?", "Hello there I am SungJinWoo...nice to meet u")
    response = response.replace("Have the control right." , "@The_Pirate_Hunter is my owner.")
    response = response.replace("Hi, my friend, what can I do for you today?" , "Hi, My name is SungJinWoo Nice to meet you")

    pro = response
    if not "en" in lan and not lan == "":
        pro = translator.translate(pro, dest=lan)
        pro = pro.text
    try:
        await daisyx.send_chat_action(message.chat.id, "typing")
        await message.reply_text(pro)
    except CFError:
        return


@daisyx.on_message(
    filters.regex("SungJinwoo|Sung Jin woo")
    & ~filters.bot
    & ~filters.via_bot
    & ~filters.forwarded
    & ~filters.reply
    & ~filters.channel
    & ~filters.edited
)
async def inuka(client, message):
    msg = message.text
    if msg.startswith("/") or msg.startswith("@"):
        message.continue_propagation()
    u = msg.split()
    emj = extract_emojis(msg)
    msg = msg.replace(emj, "")
    if (
        [(k) for k in u if k.startswith("@")]
        and [(k) for k in u if k.startswith("#")]
        and [(k) for k in u if k.startswith("/")]
        and re.findall(r"\[([^]]+)]\(\s*([^)]+)\s*\)", msg) != []
    ):

        h = " ".join(filter(lambda x: x[0] != "@", u))
        km = re.sub(r"\[([^]]+)]\(\s*([^)]+)\s*\)", r"", h)
        tm = km.split()
        jm = " ".join(filter(lambda x: x[0] != "#", tm))
        hm = jm.split()
        rm = " ".join(filter(lambda x: x[0] != "/", hm))
    elif [(k) for k in u if k.startswith("@")]:

        rm = " ".join(filter(lambda x: x[0] != "@", u))
    elif [(k) for k in u if k.startswith("#")]:
        rm = " ".join(filter(lambda x: x[0] != "#", u))
    elif [(k) for k in u if k.startswith("/")]:
        rm = " ".join(filter(lambda x: x[0] != "/", u))
    elif re.findall(r"\[([^]]+)]\(\s*([^)]+)\s*\)", msg) != []:
        rm = re.sub(r"\[([^]]+)]\(\s*([^)]+)\s*\)", r"", msg)
    else:
        rm = msg
        # print (rm)
    try:
        lan = translator.detect(rm)
        lan = lan.lang
    except:
        return
    test = rm
    if not "en" in lan and not lan == "":
        try:
            test = translator.translate(test, dest="en")
            test = test.text
        except:
            return

    # test = emoji.demojize(test.strip())

    test = test.replace("Sung", "Aco")
    test = test.replace("Sung", "Aco")
    test = test.replace("I was created by @The_Pirate_hunter", "I made myself")
    test = test.replace("Hello there I am SungJinWoo...nice to meet u", "Hi, my friend! Do you want me to tell you a joke?")
    test = test.replace("@The_Pirate_Hunter is my owner" , "Have the control right.")
    test = test.replace("Hi, My name is SungJinWoo Nice to meet you." , "Hi, my friend, what can I do for you today?")

    response = await lunaQuery(test, message.from_user.id if message.from_user else 0)
    response = response.replace("Aco", "Sung")
    response = response.replace("aco", "Sung")
    response = response.replace("I made myself", "I was Created by @The_Pirate_Hunter")
    response = response.replace("Hi, my friend! Do you want me to tell you a joke?", "Hello there I am SungJinWoo...nice to meet u")
    response = response.replace("Have the control right." , "@The_Pirate_Hunter is my owner.")
    response = response.replace("Hi, my friend, what can I do for you today?" , "Hi, My name is SungJinWoo Nice to meet you")

    pro = response
    if not "en" in lan and not lan == "":
        try:
            pro = translator.translate(pro, dest=lan)
            pro = pro.text
        except Exception:
            return
    try:
        await daisyx.send_chat_action(message.chat.id, "typing")
        await message.reply_text(pro)
    except CFError:
        return

__help__ = """
*IGRIS-X Chatbot Supports many Languages.*

 ➢ /chatbot [ON/OFF]: Enables and disables AI Chat mode (EXCLUSIVE)
 ➢ /chatbot EN : Enables English only chatbot
 
"""

__mod_name__ = "ChatBot"
