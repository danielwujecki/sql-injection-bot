import logging

from telegram import Update
from telegram.error import BadRequest
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

from . import send
from . import utils
from .. import database
from ..configuration import Config
from ..database.dbinterface import DBInterface


logger = logging.getLogger('sqlbot.updater')


async def start(db: DBInterface, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user:
        logger.error("/start: could not store a user.")
        return

    chatID    = update.effective_chat.id
    firstname = update.effective_user.first_name
    lastname  = update.effective_user.last_name
    username  = update.effective_user.username

    if database.get.chat_known(db, chatID):
        reply = "Du hast den Start-Befehl erneut ausgeführt!"
        inlay = "erneut "
        utils.update_chat(db, update)
    else:
        reply = "Willkommen beim SqlBot!\nDu wirst bald einer Gruppe zugewiesen."
        inlay = ""
        database.insert.chat(db, chatID, firstname, lastname, username)

    await update.message.reply_text(reply)

    info = f"Nutzer hat den Start-Befehl {inlay}ausgeführt: {firstname}"
    if lastname:
        info += f" {lastname}"
    if username:
        info += f" @{username}"
    await send.msg_to_mods(db, context.bot, info)


async def me(db: DBInterface, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    utils.update_chat(db, update)

    info = database.get.chat_info(db, update.effective_chat.id)
    if not info:
        logger.warning(f"Unknown user: {update.effective_chat.id}")
        await update.message.reply_text("Please issue /start command again!")
        return

    reply = "Du besitzt nicht die nötigen Rechte um diesen Befehl auszuführen."
    if info[2]:
        surname = f" {info[1]}" if info[1] else ""
        status  = f"Status: '{info[4]}'" if info[4] else "Kein status gesetzt."
        reply   = f"{info[0]}{surname}\nNutzergruppe {info[2]}: {info[3]}\n{status}"

    await update.message.reply_text(reply)


async def groups(db: DBInterface, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    utils.update_chat(db, update)

    if not await utils.check_permissions(db, 1, update):
        return

    reply  = "Es gibt folgende Nutzergruppen:\n"
    reply += "\n".join(map(
        lambda x: f"Gruppe {x[0]} - {x[1]}",
        database.get.groups(db)
    ))
    await update.message.reply_text(reply)


async def setstatus(db: DBInterface, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    utils.update_chat(db, update)

    if not await utils.check_permissions(db, 1, update):
        return

    if len(context.args) < 1:
        reply = "Korrekter Befehl:\n/setstatus <text>"
        await update.message.reply_text(reply)
        return

    chatID = update.effective_chat.id
    if not database.update.chat_status(db, chatID, " ".join(context.args)):
        logger.error(f"Something went wrong while updating status for user with id '{chatID}'")
        await update.message.reply_text("Fehler: status konnte nicht gesetzt werden.")
        return

    await update.message.reply_text("Status gesetzt.")


async def help_cmd(db: DBInterface, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    utils.update_chat(db, update)

    chatID = update.effective_chat.id
    chat_info = database.get.chat_info(db, chatID)
    if not chat_info:
        logger.warning(f"Unknown user: {update.effective_chat.id}")
        await update.message.reply_text("Please issue /start command again!")
        return
    if not chat_info[2]:
        logger.error(f"No groupID for the following chat: {chat_info}")
        return

    reply  = "Dieser Bot dient zur Demonstration von Sicherheitslücken.\n"
    reply += "/start - Nutzerupdate\n"
    reply += "/me - Informationen über mich\n"
    reply += "/groups - Gruppenübersicht\n"
    reply += "/setstatus - Status setzen\n"
    reply += "/help - Hilfe und Befehlsübersicht\n\n"
    if chat_info[2] > 1:
        reply += "/listusers - Nutzerliste\n"
        reply += "/setusergroup - Nutzergruppe setzen\n"
        reply += "/sendmsg - sende Nachricht an Nutzer"

    await update.message.reply_text(reply)


async def listusers(db: DBInterface, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    def fetch2chat(chat: tuple):
        chatid, groupid, firstname, lastname, username = chat
        lastname = f" {lastname}" if lastname else ""
        username = f" @{username}" if username else ""
        res = f"{firstname}{lastname}{username}\nchatID: {chatid}; groupID: {groupid}"
        return res

    utils.update_chat(db, update)

    if not await utils.check_permissions(db, 2, update):
        return

    reply = "\n----------\n".join(map(fetch2chat, database.get.chats(db)))
    await update.message.reply_text(reply)


async def setusergroup(db: DBInterface, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    utils.update_chat(db, update)

    chat_info = database.get.chat_info(db, update.effective_chat.id)
    if not chat_info:
        logger.warning(f"Unknown user: {update.effective_chat.id}")
        await update.message.reply_text("Please issue /start command again!")
        return

    own_groupID = chat_info[2]
    if own_groupID < 2:
        await update.message.reply_text("Du besitzt nicht die nötigen Rechte um diesen Befehl auszuführen.")
        return

    if len(context.args) != 2:
        reply = "Korrekter Befehl:\n/setusergroup <chatID> <groupID>"
        await update.message.reply_text(reply)
        return

    chatID, groupID = None, None
    try:
        chatID, groupID = int(context.args[0]), int(context.args[1])
    except ValueError as ve:
        await update.message.reply_text("Error during a message. Check logs!")
        logger.error("Error while setting usergroup.", exc_info=ve)
        return

    if not chatID or not database.get.chat_known(db, chatID):
        await update.message.reply_text("Ungültige chatID.")
        return

    if groupID is None or groupID not in range(4):
        await update.message.reply_text("Ungültige groupID.")
        return

    if database.get.chat_info(db, chatID)[2] >= own_groupID:
        await update.message.reply_text("Not allowed to modify groupID of a equal or higher group.")
        return

    if database.update.chat_groupID(db, chatID, groupID):
        await update.message.reply_text("Befehl erfolgreich.")
        logger.info(f"Updated usergroup to {groupID} in chat with chatID '{chatID}'.")

        info  = f"Du wurdest der Nutzergruppe {groupID} zugewiesen.\n"
        info += "Mehr Infos durch den Befehl: /groups"
        await context.bot.send_message(chat_id=chatID, text=info)
    else:
        await update.message.reply_text("Could not update usergroup.")
        logger.error("Could not update usergroup to {groupID} in chat with chatID '{chatID}'.")


async def sendmsg(db: DBInterface, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    utils.update_chat(db, update)

    if not await utils.check_permissions(db, 2, update):
        return

    if len(context.args) < 1:
        reply = "Korrekter Befehl:\n/sendmsg <text>"
        await update.message.reply_text(reply)
        return

    text  = " ".join(context.args).replace("RET ", "\n").replace("RET", "\n")
    chats = database.get.chatids_with_groupid(db, 1)

    try:
        chats.remove(update.effective_chat.id)
    except ValueError:
        logger.error("ValueError in 'sendmsg'")

    for chatID in chats:
        try:
            await context.bot.send_message(chat_id=chatID, text=text)
        except BadRequest as err:
            logmsg = f"BadRequest for user with chatid = '{chatID}'."
            logger.error(logmsg)
            await update.message.reply_text(logmsg)
        except Exception as err:
            logmsg = f"Exception for user with chatid = '{chatID}'."
            logger.error(logmsg, exc_info=err)
            await update.message.reply_text(logmsg)

    await update.message.reply_text("Befehl ausgeführt.")


async def unknown(db: DBInterface, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    utils.update_chat(db, update)
    await update.message.reply_text("Sorry, dieser Befehl ist unbekannt. /help")


async def forward_message(db: DBInterface, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    utils.update_chat(db, update)

    chatID    = update.effective_chat.id
    firstname = update.effective_user.first_name
    lastname  = update.effective_user.last_name
    username  = update.effective_user.username
    modids    = database.get.chatids_with_groupid(db, 2)

    if chatID in modids:
        return

    lastname = f" {lastname}" if lastname else ""
    username = f" @{username}" if username else ""
    msg      = f"{firstname}{lastname}{username}:\n{update.message.text}"

    for chatID in modids:
        await context.bot.send_message(chat_id=chatID, text=msg)


async def error_handler(db: DBInterface, _: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling an update:", exc_info=context.error)
    await send.msg_to_mods(db, context.bot, "Error during a message. Check logs!")


def configure_bot(cfg: Config, db: DBInterface) -> Application:
    application = ApplicationBuilder().token(cfg.telegram_token).build()

    application.add_handler(CommandHandler('start',                         lambda U, c: start(db, U, c)))
    application.add_handler(CommandHandler('me',                            lambda U, c: me(db, U, c)))
    application.add_handler(CommandHandler('groups',                        lambda U, c: groups(db, U, c)))
    application.add_handler(CommandHandler('setstatus',                     lambda U, c: setstatus(db, U, c)))
    application.add_handler(CommandHandler('help',                          lambda U, c: help_cmd(db, U, c)))

    application.add_handler(CommandHandler('listusers',                     lambda U, c: listusers(db, U, c)))
    application.add_handler(CommandHandler('setusergroup',                  lambda U, c: setusergroup(db, U, c)))
    application.add_handler(CommandHandler('sendmsg',                       lambda U, c: sendmsg(db, U, c)))

    application.add_handler(MessageHandler(filters.COMMAND,                 lambda U, c: unknown(db, U, c)))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lambda U, c: forward_message(db, U, c)))
    application.add_error_handler(lambda U, c: error_handler(db, U, c))

    return application
