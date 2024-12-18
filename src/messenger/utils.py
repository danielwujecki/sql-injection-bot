from telegram import Update

from .. import database
from ..database.dbinterface import DBInterface


async def check_permissions(db: DBInterface, groupID: int, update: Update):
    chat_groupID = database.get.chat_info(db, update.effective_chat.id)[2]
    if not chat_groupID or chat_groupID < groupID:
        await update.message.reply_text("Du besitzt nicht die nötigen Rechte um diesen Befehl auszuführen.")
        return False
    return True


def update_chat(db: DBInterface, update: Update):
    chatID    = update.effective_chat.id
    firstname = update.effective_user.first_name
    lastname  = update.effective_user.last_name
    username  = update.effective_user.username
    database.update.chat(db, chatID, firstname, lastname, username)
