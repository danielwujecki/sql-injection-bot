import logging

from .dbinterface import DBInterface


logger = logging.getLogger("sqlbot.database.update")


def chat_groupID(db: DBInterface, chatID: int, groupID: int) -> bool:
    sql_str = "UPDATE chat SET groupid = %s WHERE chatid = %s;"
    return bool(db.execute(sql_str, (groupID, chatID)) and db.commit())


def chat_status(db: DBInterface, chatID: int, status: str) -> bool:
    sql_str = "UPDATE chat SET status = %s WHERE chatid = %s;"
    return bool(db.execute(sql_str, (status, chatID)) and db.commit())


def chat_status_bad(db: DBInterface, chatID: int, status: str) -> bool:
    sql_str = f"UPDATE chat SET status = '{status}' WHERE chatid = {chatID};"
    logger.info(f"Update users status: {sql_str}")
    return bool(db.execute(sql_str) and db.commit())


def chat(db: DBInterface, chatID: int, firstname: str, lastname: str, username: str) -> bool:
    sql_str = """
        UPDATE chat SET firstname = %s, lastname = %s, username = %s
        WHERE chatid = %s;
    """
    if db.execute(sql_str, (firstname, lastname, username, chatID)):
        return db.commit()
    else:
        logger.debug("Failed to update chat.")
        return False
