from SungJinwooRobot import pgram
from SungJinwooRobot.utils.dbfunctions import (update_karma, get_karma, get_karmas,
                                   int_to_alpha, alpha_to_int)
from SungJinwooRobot.utils.filter_groups import karma_positive_group, karma_negative_group
from pyrogram import filters


regex_upvote = r"^((?i)\+\+\+|\+\+\+\+|\+\+\+\+\+|\+1|awesome \+\+\+|nice \+\+\+|cool \+\+\+|cool \+\+|cool \+|nice \+\+|nice \+|lmao 😂)$"
regex_downvote = r"^((?i)\-\-\-\-\-|not nice \-\-\-\-\-|)$"


@pgram.on_message(
    filters.text
    & filters.group
    & filters.incoming
    & filters.reply
    & filters.regex(regex_upvote)
    & ~filters.via_bot
    & ~filters.bot
    & ~filters.edited,
    group=karma_positive_group
)

async def upvote(_, message):
    if message.reply_to_message.from_user.id == message.from_user.id:
        return
    chat_id = message.chat.id
    user_id = message.reply_to_message.from_user.id
    user_mention = message.reply_to_message.from_user.mention
    current_karma = await get_karma(chat_id, await int_to_alpha(user_id))
    if current_karma:
        current_karma = current_karma['karma']
        karma = current_karma + 1
        new_karma = {"karma": karma}
        await update_karma(chat_id, await int_to_alpha(user_id), new_karma)
    else:
        karma = 1
        new_karma = {"karma": karma}
        await update_karma(chat_id, await int_to_alpha(user_id), new_karma)
    await message.reply_text(
        f'Increased Reputation of {user_mention} By 1 \nTotal Points: {karma}'
    )


@pgram.on_message(
    filters.text
    & filters.group
    & filters.incoming
    & filters.reply
    & filters.regex(regex_downvote)
    & ~filters.via_bot
    & ~filters.bot
    & ~filters.edited,
    group=karma_negative_group
)

async def downvote(_, message):
    if message.reply_to_message.from_user.id == message.from_user.id:
        return
    chat_id = message.chat.id
    user_id = message.reply_to_message.from_user.id
    user_mention = message.reply_to_message.from_user.mention
    current_karma = await get_karma(chat_id, await int_to_alpha(user_id))
    if current_karma:
        current_karma = current_karma['karma']
        karma = current_karma - 1
        new_karma = {"karma": karma}
        await update_karma(chat_id, await int_to_alpha(user_id), new_karma)
    else:
        karma = 1
        new_karma = {"karma": karma}
        await update_karma(chat_id, await int_to_alpha(user_id), new_karma)
    await message.reply_text(
        f'Decreased Reputation Of {user_mention} By 1 \nTotal Points: {karma}'
    )


@pgram.on_message(filters.command("reputation") & filters.group)

async def karma(_, message):
    chat_id = message.chat.id

    if not message.reply_to_message:
        karma = await get_karmas(chat_id)
        msg = f"**Reputation list of {message.chat.title}:- **\n"
        limit = 0
        karma_dicc = {}
        for i in karma:
            user_id = await alpha_to_int(i)
            user_karma = karma[i]['karma']
            karma_dicc[str(user_id)] = user_karma
            karma_arranged = dict(
                sorted(karma_dicc.items(), key=lambda item: item[1], reverse=True))
        for user_idd, karma_count in karma_arranged.items():
            if limit > 9:
                break
            try:
                user_name = (await pgram.get_users(int(user_idd))).username
            except Exception:
                continue
            msg += f"{user_name} : `{karma_count}`\n"
            limit += 1
        await message.reply_text(msg)
    else:
        user_id = message.reply_to_message.from_user.id
        karma = await get_karma(chat_id, await int_to_alpha(user_id))
        if karma:
            karma = karma['karma']
            await message.reply_text(f'**Total Points**: __{karma}__')
        else:
            karma = 0
            await message.reply_text(f'**Total Points**: __{karma}__')

__mod_name__ = "Reputation"
__help__ = """*Upvote* - Use upvote keywords like "+++", "++++", "+++++", "cool +++", "nice +++", "awesome +++", "lmao 😂" to upvote a message.

*Downvote* - Use downvote keywords like "not nice ---", "---", etc. to downvote a message.

Reply to a message with `/reputation` to check a user's reputation.
Send `/reputation` without replying to any message to chek reputation list of top 10 users."""

