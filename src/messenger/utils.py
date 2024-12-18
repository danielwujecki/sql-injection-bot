from telegram import Update

from .. import database
from ..database.dbinterface import DBInterface


async def check_permissions(db: DBInterface, groupID: int, update: Update) -> bool:
    chat_info = database.get.chat_info(db, update.effective_chat.id)
    if not chat_info or chat_info[2] < groupID:
        await update.message.reply_text("Du besitzt nicht die nötigen Rechte um diesen Befehl auszuführen.")
        return False
    return True


def update_chat(db: DBInterface, update: Update) -> bool:
    chatID    = update.effective_chat.id
    firstname = update.effective_user.first_name
    lastname  = update.effective_user.last_name
    username  = update.effective_user.username
    return database.update.chat(db, chatID, firstname, lastname, username)
