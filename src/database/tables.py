import sys
import logging
from .dbinterface import DBInterface


logger = logging.getLogger("sqlbot.database.tables")


def drop_all_tables(db: DBInterface):
    sql_str = """
        DROP TABLE IF EXISTS chat;
        DROP TABLE IF EXISTS usergroup;
    """
    db.execute(sql_str)
    db.commit()


def create_table_usergroup(db: DBInterface):
    sql_str = """
        CREATE TABLE usergroup (
            groupID SMALLINT CHECK (groupID <= 5 AND groupID >= 0) PRIMARY KEY,
            description TEXT NOT NULL
        );
    """
    db.execute(sql_str)

    sql_str = """
        INSERT INTO usergroup VALUES(0, 'Gast');
        INSERT INTO usergroup VALUES(1, 'Nutzer');
        INSERT INTO usergroup VALUES(2, 'Moderator');
        INSERT INTO usergroup VALUES(3, 'Admin');
    """
    db.execute(sql_str)


def create_table_chat(db: DBInterface):
    sql_str = """
        CREATE TABLE chat (
            chatID BIGINT PRIMARY KEY,
            groupID SMALLINT NOT NULL,
            firstName TEXT NOT NULL,
            lastName TEXT,
            username TEXT,
            FOREIGN KEY (groupID) REFERENCES usergroup(groupID)
        );
    """
    db.execute(sql_str)


def initialize_database(db: DBInterface):
    drop_all_tables(db)

    create_table_usergroup(db)
    create_table_chat(db)

    db.commit()

    logger.warning("Database (re)initialized.")


def check_table_existance(db: DBInterface):
    sql_str = "SELECT to_regclass('public.chat');"
    db.execute(sql_str)
    table_chat = db.fetchall()[0][0]

    sql_str = "SELECT to_regclass('public.usergroup');"
    db.execute(sql_str)
    table_usergroup = db.fetchall()[0][0]

    if table_chat is None or table_usergroup is None:
        logger.critical("Database tables missing. Need to be (re)initialized.")
        db.close()
        sys.exit(1)
