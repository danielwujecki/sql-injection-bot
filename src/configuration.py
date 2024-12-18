"""
This module provides the Config class to store the configuration tree

Furthermore utility functions to read and create a Config object
from commandline inputs and a YAML file are provided
"""

import os
import sys
import yaml
import logging
import argparse


logger = logging.getLogger('sqlbot.configuration')


class Config(dict):
    """
    Fancy Configuration class
    Makes it possible to access a dictionary by member attributes.
    Example:
        cfg = Config({'a': 1, 'b': {'c': 2}})
        print(cfg.a) --> 1
        print(cfg.b.c) --> 2
    """
    @classmethod
    def _create_config_tree(cls, input_dict: dict):
        for key, val in input_dict.items():
            if isinstance(val, dict):
                input_dict[key] = cls(val)
        return input_dict

    def __init__(self, input_dict: dict):
        super().__init__(
            self._create_config_tree(input_dict)
        )

    def __getattr__(self, name):
        if name in self:
            return self[name]
        return None

    def __setattr__(self, key, val):
        if isinstance(val, dict):
            self[key] = Config(val)
        else:
            self[key] = val

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError(f"No such attribute: {name}")


def getcfg(filename: str = None):
    """
    Asserts that config file is given as a command line parameter.
    config.yml is loaded and custom Config object is returned.
    """

    if filename is None:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--config",
            type=str,
            required=True,
            help="Path to (.yml) config file."
        )
        configargs = parser.parse_args()
        filename = configargs.config

    if not os.path.isfile(filename):
        logger.critical("Config file not found. Exiting.")
        sys.exit(1)

    # Read config file.
    with open(filename, 'r', encoding='UTF-8') as fp:
        cfg_dict = yaml.load(fp, Loader=yaml.FullLoader)
        cfg = Config(cfg_dict)

    cfg['configuration_path'] = filename
    return cfg


def check_cfg_mandatory(cfg: Config):
    """check if mandatory config settings are properly set"""

    default_msg = "'{}' not set in configuration. Using default value '{}'"

    if 'loglevel' not in cfg:
        cfg['loglevel'] = 'debug'
        logger.warning(default_msg.format('loglevel', cfg.loglevel))
    if 'logfmt' not in cfg:
        cfg['logfmt'] = '[%(levelname)s] %(asctime)s - %(name)s: %(message)s'
        logger.warning(default_msg.format('logfmt', cfg.logfmt))
    if 'ascfmt' not in cfg:
        cfg['ascfmt'] = '%d-%m-%y %H:%M:%S'
        logger.warning(default_msg.format('ascfmt', cfg.ascfmt))

    if 'db_name' not in cfg:
        cfg['db_name'] = 'postgres'
        logger.warning(default_msg.format('db_name', cfg.db_name))
    if 'db_user' not in cfg:
        cfg['db_user'] = 'postgres'
        logger.warning(default_msg.format('db_user', cfg.db_user))
    if 'db_password' not in cfg:
        cfg['db_password'] = ''
        logger.warning(default_msg.format('db_password', cfg.db_password))
    if 'db_host' not in cfg:
        cfg['db_host'] = 'localhost'
        logger.warning(default_msg.format('db_host', cfg.db_host))
    if 'db_port' not in cfg:
        cfg['db_port'] = '5432'
        logger.warning(default_msg.format('db_port', cfg.db_port))

    if 'telegram_token' not in cfg or not isinstance(cfg.telegram_token, str):
        logger.critical("'telegram_token' not a string in configuration. Exiting.")
        sys.exit(1)


def check_cfg_datatype(cfg: Config):
    """check datatype of config settings"""
    if isinstance(cfg.loglevel, str):
        cfg.loglevel = getattr(logging, cfg.loglevel.upper())

    attributes = [
        'logfmt', 'ascfmt',
        'db_name', 'db_user', 'db_password', 'db_host', 'db_port'
    ]
    for attr in attributes:
        setattr(cfg, attr, str(getattr(cfg, attr)))


def check_cfg_optional(cfg: Config):
    """check optional config settings"""
    if 'db_init' in cfg:
        if not isinstance(cfg.db_init, bool):
            logger.critical("'db_init' not a bool. Exiting.")
            sys.exit(1)


def check_cfg(cfg: Config):
    """
    Verifies that Config object contains all required
    attributes of corresponding datatype
    """
    check_cfg_mandatory(cfg)
    check_cfg_datatype(cfg)
    check_cfg_optional(cfg)


if __name__ == "__main__":
    # Debugging
    config = getcfg()
    check_cfg(config)
    print(config.configuration_path)
    print(config)
