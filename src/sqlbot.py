"""
@author: danielwujecki
"""

import sys
import logging
import logging.handlers

from . import database
from . import messenger
from . import configuration


logger = logging.getLogger('sqlbot')


def configure_logging(cfg):
    """
    setup logging module
    """

    fmt = logging.Formatter(fmt=cfg.logfmt, datefmt=cfg.ascfmt)
    sh  = logging.StreamHandler(stream=sys.stdout)
    sh.setLevel(cfg.loglevel)
    sh.setFormatter(fmt)
    rlogger = logging.getLogger("")
    rlogger.setLevel(cfg.loglevel)
    rlogger.addHandler(sh)

    logging.getLogger("httpx").setLevel(logging.WARNING)


def configure_db(cfg):
    db = database.dbinterface.DBInterface(cfg)

    if cfg.db_init:
        database.tables.table_create_all(db, ric_csv=cfg.db_rics)
        logmsg = "Please set 'db_init: false' in your config and restart."
        print(logmsg)
        logger.warning(logmsg)
        sys.exit(0)

    database.tables.check_table_existance(db)
    return db


def launch():
    """
    Read configuration, setup logging module,
    launch radio receiver and start processing messages
    """

    cfg = configuration.getcfg()
    configuration.check_cfg(cfg)

    configure_logging(cfg)
    db = configure_db(cfg)

    application = messenger.bot.configure_bot(cfg, db)
    application.run_polling()

    db.close()
    logger.info("Shutting down")
