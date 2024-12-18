import logging

from .dbinterface import DBInterface


logger = logging.getLogger("sqlbot.database.get")


def chat_known(db: DBInterface, chatID: int) -> bool:
    sql_str = "SELECT count(*) FROM chat WHERE chatID = %s;"
    db.execute(sql_str, (chatID,))
    return bool(db.fetchall()[0][0])


def chat_info(db: DBInterface, chatID: int):
    sql_str = """
        SELECT c.firstname, c.lastname, u.groupid, u.description, c.status
        FROM chat c INNER JOIN usergroup u on u.groupid = c.groupid
        WHERE chatid = %s;
    """
    db.execute(sql_str, (chatID,))
    res = db.fetchall()

    logger.debug(f"chat_info(...): {res}")

    if isinstance(res, list) and len(res) > 0:
        return res[0]
    return None


def groups(db: DBInterface):
    sql_str = "SELECT * FROM usergroup ORDER BY groupid;"
    db.execute(sql_str)
    return db.fetchall()


def chatids_with_groupid(db: DBInterface, groupid: int):
    sql_str = "SELECT chatid FROM chat WHERE groupid >= %s;"
    db.execute(sql_str, (groupid,))
    return list(map(lambda x: x[0], db.fetchall()))


def chats(db: DBInterface):
    sql_str = """
        SELECT chatid, groupid, firstname, lastname, username
        FROM chat
        ORDER BY groupid;
    """
    db.execute(sql_str)
    return db.fetchall()
