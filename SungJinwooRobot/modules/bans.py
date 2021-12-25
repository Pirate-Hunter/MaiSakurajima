import html

from telegram import ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, Filters, run_async
from telegram.utils.helpers import mention_html

from SungJinwooRobot import (
    DEV_USERS,
    LOGGER,
    OWNER_ID,
    DRAGONS,
    DEMONS,
    TIGERS,
    WOLVES,
    dispatcher,
)
from SungJinwooRobot.modules.disable import DisableAbleCommandHandler
from SungJinwooRobot.modules.helper_funcs.chat_status import (
    bot_admin,
    can_restrict,
    connection_status,
    is_user_admin,
    is_user_ban_protected,
    is_user_in_chat,
    user_can_ban,
    can_delete,
)
from SungJinwooRobot.modules.helper_funcs.extraction import extract_user_and_text
from SungJinwooRobot.modules.helper_funcs.string_handling import extract_time
from SungJinwooRobot.modules.log_channel import gloggable, loggable
from SungJinwooRobot.modules.helper_funcs.anonymous import user_admin, AdminPerms

@connection_status
@bot_admin
@can_restrict
@user_admin(AdminPerms.CAN_RESTRICT_MEMBERS)
@user_can_ban
@loggable
def ban(update: Update, context: CallbackContext):  # sourcery no-metrics
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    message = update.effective_message  # type: Optional[Message]
    args = context.args
    bot = context.bot
    log_message = ""
    reason = ""
    if message.reply_to_message and message.reply_to_message.sender_chat:
        r = bot._request.post(bot.base_url + '/banChatSenderChat', {
            'sender_chat_id': message.reply_to_message.sender_chat.id,
            'chat_id': chat.id
        },
                              )
        if r:
            message.reply_text("Channel {} was banned from {}".format(
                html.escape(message.reply_to_message.sender_chat.title),
                html.escape(chat.title)
            ),
                parse_mode="html"
            )
        else:
            message.reply_text("Failed to ban this channel")
        return

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("I doubt that's a user.")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise

    if user_id == bot.id:
        message.reply_text("Oh yeah, ban myself, noob!")
        return log_message

    if is_user_ban_protected(chat, user_id, member) and user not in DEV_USERS:
        if user_id == OWNER_ID:
            message.reply_text(
                "Trying to put me against a God level Hunter huh?")
            return log_message
        elif user_id in DEV_USERS:
            message.reply_text("I can't act against our own.")
            return log_message
        elif user_id in DRAGONS:
            message.reply_text(
                "Fighting this A-RANK HUNTER here will put civilian lives at risk.")
            return log_message
        elif user_id in DEMONS:
            message.reply_text(
                "Bring an order from Hunter Association to fight a B-RANK HUNTER."
            )
            return log_message
        elif user_id in TIGERS:
            message.reply_text(
                "Bring an order from Hunter Association to fight a C-RANK HUNTER."
            )
            return log_message
        elif user_id in WOLVES:
            message.reply_text("D-RANK HUNTER abilities make them ban immune!")
            return log_message
        else:
            message.reply_text("This user has immunity and cannot be banned.")
            return log_message

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#BANNED\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )
    if reason:
        log += "\n<b>Reason:</b> {}".format(reason)

    try:
        chat.ban_member(user_id)
        # bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        reply = (
            f"<b>Banned❗</b>\n"
            f"<b>• User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
        )
        if reason:
            reply += f"\n<b>• Reason:</b> \n{html.escape(reason)}"
        bot.sendMessage(
            chat.id,
            reply,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Unban❗", callback_data=f"unban_un={user_id}"
                        ),
                        InlineKeyboardButton(text="Delete❓", callback_data="unban_del"),
                    ]
                ]
            ),
            parse_mode=ParseMode.HTML,
        )
        return log

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text("Banned!", quote=False)
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR banning user %s in chat %s (%s) due to %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("Uhm...that didn't work...")

    return log_message

@bot_admin
@can_restrict
@user_admin(AdminPerms.CAN_RESTRICT_MEMBERS)
@loggable
def dban(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    message = update.effective_message  # type: Optional[Message]
    args = context.args
    bot = context.bot


    #if user_can_ban(chat, user, context.bot.id) is False:
    #    message.reply_text("You don't have enough rights to ban users!")
    #    return ""

    if message.reply_to_message:
        user = update.effective_user  # type: Optional[User]
        chat = update.effective_chat  # type: Optional[Chat]
        if can_delete(chat, bot.id):
            update.effective_message.reply_to_message.delete()
    else:
        message.reply_text("You have to reply to a message to delete it and ban the user.")
        return ""

    user_id, reason = extract_user_and_text(message, args)

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user")
            return ""
        else:
            raise

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("I'm not gonna ban an admin, don't make fun of yourself!")
        return ""

    if user_id == context.bot.id:
        message.reply_text("I'm not gonna ban myself, that's pretty dumb idea!")
        return ""
    
    if user_id == 777000 or user_id == 1087968824:
        message.reply_text(str(user_id) + " is an account reserved for telegram, I cannot ban it!")
        return ""            

    log = (
        "<b>{}:</b>"
        "\n#BANNED"
        "\n<b>Admin:</b> {}"
        "\n<b>User:</b> {} (<code>{}</code>)".format(   
            html.escape(chat.title),
            mention_html(user.id, user.first_name),
            mention_html(member.user.id, member.user.first_name),
            member.user.id,
        )
    )
    if reason:
        log += "\n<b>Reason:</b> {}".format(reason)

    try:
        chat.ban_member(user_id)
        # bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        reply = (
            f"<b>Banned❗</b>\n"
            f"<b>• User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
        )
        if reason:
            reply += f"\n<b>• Reason:</b> \n{html.escape(reason)}"
        bot.sendMessage(
            chat.id,
            reply,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Unban❗", callback_data=f"unban_un={user_id}"
                        ),
                        InlineKeyboardButton(text="Delete❓", callback_data="unban_del"),
                    ]
                ]
            ),
            parse_mode=ParseMode.HTML,
        )
        return log

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text("Banned!", quote=False)
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR banning user %s in chat %s (%s) due to %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("Uhm...that didn't work...")

    return log_message

@connection_status
@bot_admin
@can_restrict
@user_admin(AdminPerms.CAN_RESTRICT_MEMBERS)
@user_can_ban
@loggable
def sban(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot = context.bot
    args = context.args
    user_id, reason = extract_user_and_text(message, args)
    update.effective_message.delete()
    if not user_id:
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            return log_message
        else:
            raise

    if user_id == bot.id:
        return log_message

    if is_user_ban_protected(chat, user_id, member):
        return log_message
      
    if user_id == 777000 or user_id == 1087968824:
        return log_message
      
    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#SBANNED\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )
    if reason:
        log += "\n<b>Reason:</b> {}".format(reason)

    try:
        chat.kick_member(user_id)
        return log

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception("ERROR banning user %s in chat %s (%s) due to %s",
                             user_id, chat.title, chat.id, excp.message)
    return log_message


@connection_status
@bot_admin
@can_restrict
@user_admin(AdminPerms.CAN_RESTRICT_MEMBERS)
@user_can_ban
@loggable
def temp_ban(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("I doubt that's a user.")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user.")
            return log_message
        else:
            raise

    if user_id == bot.id:
        message.reply_text("I'm not gonna BAN myself, are you crazy?")
        return log_message

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("I don't feel like it.")
        return log_message

    if not reason:
        message.reply_text("You haven't specified a time to ban this user for!")
        return log_message

    split_reason = reason.split(None, 1)

    time_val = split_reason[0].lower()
    if len(split_reason) > 1:
        reason = split_reason[1]
    else:
        reason = ""

    bantime = extract_time(message, time_val)

    if not bantime:
        return log_message

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        "#TEMP BANNED\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}\n"
        f"<b>Time:</b> {time_val}"
    )
    if reason:
        log += "\n<b>Reason:</b> {}".format(reason)

    try:
        chat.ban_member(user_id, until_date=bantime)
        reply_msg = (
            f"❗<b>Time Banned</b>\n"
            f"<b>• User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}\n"
            f"<b>• Banned for: {time_val}</b>"
        )
        if reason:
            reply_msg += f"\n<code> </code><b>• Reason:</b> {html.escape(reason)}"

        # bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        bot.sendMessage(
            chat.id,
            reply_msg,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Unban❗", callback_data=f"unban_un={user_id}"
                        ),
                        InlineKeyboardButton(text="Delete❓", callback_data="unban_del"),
                    ]
                ]
            ),
            parse_mode=ParseMode.HTML,
        )
        return log

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text(
                f"Banned! User will be banned for {time_val}.", quote=False
            )
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR banning user %s in chat %s (%s) due to %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("Well damn, I can't ban that user.")

    return log_message

  
@connection_status
@bot_admin
@can_restrict
@user_admin(AdminPerms.CAN_RESTRICT_MEMBERS)
@user_can_ban
@loggable
def stemp_ban(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)
    update.effective_message.delete()
    if not user_id:
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            return log_message
        else:
            raise

    if user_id == bot.id:
        return log_message

    if is_user_ban_protected(chat, user_id, member):
        return log_message

    if not reason:
        message.reply_text("You haven't specified a time to ban this user for!")
        return log_message

    split_reason = reason.split(None, 1)

    time_val = split_reason[0].lower()
    if len(split_reason) > 1:
        reason = split_reason[1]
    else:
        reason = ""

    bantime = extract_time(message, time_val)

    if not bantime:
        return log_message

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        "#STEMP BANNED\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}\n"
        f"<b>Time:</b> {time_val}"
    )
    if reason:
        log += "\n<b>Reason:</b> {}".format(reason)

    try:
        chat.ban_member(user_id, until_date=bantime)
        # bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        return log

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR banning user %s in chat %s (%s) due to %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
    return log_message

  
@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def kick(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("I doubt that's a user.")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user.")
            return log_message
        else:
            raise

    if user_id == bot.id:
        message.reply_text("Yeahhh I'm not gonna do that.")
        return log_message

    if is_user_ban_protected(chat, user_id):
        message.reply_text("I really wish I could kick this user....")
        return log_message

    res = chat.unban_member(user_id)  # unban on current user = kick
    if res:
        # bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        bot.sendMessage(
            chat.id,
            f"User Kicked Woops! {mention_html(member.user.id, html.escape(member.user.first_name))}.",
            parse_mode=ParseMode.HTML)
        log = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#KICKED\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
        )
        if reason:
            log += f"\n<b>Reason:</b> {reason}"

        return log

    else:
        message.reply_text("Well damn, I can't kick that user.")

    return log_message


@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def skick(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)
    update.effective_message.delete()
    if not user_id:
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            return log_message
        else:
            raise

    if user_id == bot.id:
        return log_message

    if is_user_ban_protected(chat, user_id):
        return log_message

    res = chat.unban_member(user_id)  # unban on current user = kick
    if res:
        log = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#SKICKED\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
        )
        if reason:
            log += f"\n<b>Reason:</b> {reason}"

        return log

    return log_message
  
  
@bot_admin
@can_restrict
def kickme(update: Update, context: CallbackContext):
    user_id = update.effective_message.from_user.id
    if is_user_admin(update.effective_chat, user_id):
        update.effective_message.reply_text(
            "I wish I could... but you're an admin.")
        return

    res = update.effective_chat.unban_member(
        user_id)  # unban on current user = kick
    if res:
        update.effective_message.reply_text("*kicks you out of the group*")
    else:
        update.effective_message.reply_text("Huh? I can't :/")


@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def unban(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("I doubt that's a user.")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user.")
            return log_message
        else:
            raise

    if user_id == bot.id:
        message.reply_text("How would I unban myself if I wasn't here...?")
        return log_message

    if is_user_in_chat(chat, user_id):
        message.reply_text("Isn't this person already here??")
        return log_message

    chat.unban_member(user_id)
    message.reply_text("Yep, this user can join!")

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#UNBANNED\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )
    if reason:
        log += f"\n<b>Reason:</b> {reason}"

    return log


@connection_status
@bot_admin
@can_restrict
@gloggable
def selfunban(context: CallbackContext, update: Update) -> str:
    message = update.effective_message
    user = update.effective_user
    bot, args = context.bot, context.args
    if user.id not in DRAGONS or user.id not in TIGERS:
        return

    try:
        chat_id = int(args[0])
    except:
        message.reply_text("Give a valid chat ID.")
        return

    chat = bot.getChat(chat_id)

    try:
        member = chat.get_member(user.id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user.")
            return
        else:
            raise

    if is_user_in_chat(chat, user.id):
        message.reply_text("Aren't you already in the chat??")
        return

    chat.unban_member(user.id)
    message.reply_text("Yep, I have unbanned you.")

    

@connection_status
@bot_admin
@can_restrict
@user_admin(AdminPerms.CAN_RESTRICT_MEMBERS)
@user_can_ban
@loggable
def un_banbutton(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    query = update.callback_query
    chat = update.effective_chat
    user = update.effective_user
    if query.data != "unban_del":
        splitter = query.data.split("=")
        query_match = splitter[0]
        if query_match == "unban_un":
            user_id = splitter[1]
            if not is_user_admin(chat, int(user.id)):
                bot.answer_callback_query(
                    query.id,
                    text="You don't have enough rights to unban people",
                    show_alert=True,
                )
                return ""
            if str(user_id).startswith("-100"):
                chat.unban_sender_chat(int(user_id))
                query.message.edit_text(
                    f"Yep! <b>{user_id}</b> can send messages again!\n<b>Unbaned by:</b> {mention_html(user.id, user.first_name)}",
                    parse_mode=ParseMode.HTML,
                )
                return ("<b>{}:</b>"
                        "\n#UNBANED"
                        "\n<b>Admin:</b> {}"
                        "\n<b>User:</b> {}".format(
                    html.escape(chat.title),
                    mention_html(user.id, user.first_name),
                    user_id,
                ))
            try:
                member = chat.get_member(user_id)
            except BadRequest:
                pass

            reply_msg = (
                f"{mention_html(member.user.id, member.user.first_name)} can join again!\n"
                f"<b>Unbanned by:</b> {mention_html(user.id, user.first_name)}"
            )
            chat.unban_member(user_id)
            query.message.edit_text(
                reply_msg,
                parse_mode=ParseMode.HTML,
            )
            bot.answer_callback_query(query.id, text="Unbanned!")
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                "#UNBANNED\n"
                f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
            )

    else:
        if not is_user_admin(chat, int(user.id)):
            bot.answer_callback_query(
                query.id,
                text="You don't have enough rights to delete this message.",
                show_alert=True,
            )
            return ""
        query.message.delete()
        bot.answer_callback_query(query.id, text="Deleted!")
        return ""

__help__ = """
*Kicks:*
➢ `/kick <userhandle>`*:* Kicks a user out of the group, (via handle, or reply)
➢ `/skick <userhandle>`*:* Silently kicks a user out of the group, (via handle, or reply)
➢ `/kickme`*:* Kicks the user who used the command.
 
*Bans:*
➢ `/ban <userhandle>`*:* Bans a user. (via handle, or reply)
➢ `/sban <userhandle>`*:* Silently bans a user without leaving any message. (via handle, or reply)
➢ `/dban` <userhandle>: Bans a user and also deletes the message sent by banned user.
➢ `/tban <userhandle> x(m/h/d)`*:* Bans a user for `x` time. (via handle, or reply). `m` = `minutes`, `h` = `hours`, `d` = `days`.
➢ `/stban <userhandle> x(m/h/d)`*:* Silently bans a user for `x` time. (via handle, or reply). `m` = `minutes`, `h` = `hours`, `d` = `days`.
➢ `/unban <userhandle>`*:* Unbans a user. (via handle, or reply)

*NOTE:*
 If you set Log Channels, you will get logs of Silent kick and bans. Check *Logger* module to know more about Log Channel.
"""

BAN_HANDLER = CommandHandler("ban", ban, run_async=True)
TEMPBAN_HANDLER = CommandHandler(["tban"], temp_ban, run_async=True)
STEMPBAN_HANDLER = CommandHandler(["stban"], stemp_ban, run_async=True)
KICK_HANDLER = CommandHandler(["kick", "bonk"], kick, run_async=True)
DBAN_HANDLER = CommandHandler("dban", dban, run_async=True)
SKICK_HANDLER = CommandHandler("skick", skick, run_async=True)
UNBAN_HANDLER = CommandHandler("unban", unban, run_async=True)
ROAR_HANDLER = CommandHandler("roar", selfunban, run_async=True)
KICKME_HANDLER = DisableAbleCommandHandler(
    "kickme", kickme, filters=Filters.chat_type.groups, run_async=True)
SBAN_HANDLER = CommandHandler("sban", sban, run_async=True)

dispatcher.add_handler(BAN_HANDLER)
dispatcher.add_handler(TEMPBAN_HANDLER)
dispatcher.add_handler(STEMPBAN_HANDLER)
dispatcher.add_handler(KICK_HANDLER)
dispatcher.add_handler(DBAN_HANDLER)
dispatcher.add_handler(SKICK_HANDLER)
dispatcher.add_handler(UNBAN_HANDLER)
dispatcher.add_handler(ROAR_HANDLER)
dispatcher.add_handler(KICKME_HANDLER)
dispatcher.add_handler(SBAN_HANDLER)

__mod_name__ = "Bans"
__handlers__ = [
    BAN_HANDLER, TEMPBAN_HANDLER, STEMPBAN_HANDLER, DBAN_HANDLER, KICK_HANDLER, SKICK_HANDLER, UNBAN_HANDLER, ROAR_HANDLER,
    KICKME_HANDLER, SBAN_HANDLER
]
