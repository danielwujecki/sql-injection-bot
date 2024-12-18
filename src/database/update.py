from .dbinterface import DBInterface


def chat_groupID(db: DBInterface, chatID: int, groupID: int):
    sql_str = "UPDATE chat SET groupid = %s WHERE chatid = %s;"
    return bool(db.execute(sql_str, (groupID, chatID)) and db.commit())


def chat(db: DBInterface, chatID: int, firstname: str, lastname: str, username: str):
    sql_str = """
        UPDATE chat SET firstname = %s, lastname = %s, username = %s
        WHERE chatid = %s;
    """
    if db.execute(sql_str, (firstname, lastname, username, chatID)):
        db.commit()
