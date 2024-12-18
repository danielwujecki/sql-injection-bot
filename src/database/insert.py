from .dbinterface import DBInterface


def chat(db: DBInterface, chatID: int, firstname: str, lastname: str, username: str):
    sql_str = """
        INSERT INTO chat (chatID, groupID, firstname, lastname, username)
        VALUES (%s, 0, %s, %s, %s);
    """
    if db.execute(sql_str, (chatID, firstname, lastname, username)):
        db.commit()
