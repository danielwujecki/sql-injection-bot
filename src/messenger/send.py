import logging

from telegram import Bot

from .. import database
from ..database.dbinterface import DBInterface


logger = logging.getLogger("sqlbot.send")


async def msg_to_mods(db: DBInterface, bot: Bot, msg: str) -> None:
    modids = database.get.chatids_with_groupid(db, 2)
    for chatID in modids:
        await bot.send_message(chat_id=chatID, text=msg)

