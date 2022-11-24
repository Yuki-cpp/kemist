import appdirs
import configparser
import json
import os

from kemist2.core import logger


def get_app_dirs():
    data_dir = os.path.join(appdirs.user_data_dir("kemistdb"), "databases")
    if not os.path.exists(data_dir):
        logger.debug(f"Creating app data folder")
        os.makedirs(data_dir)

    cfg_dir = appdirs.user_config_dir("kemistdb")
    if not os.path.exists(cfg_dir):
        logger.debug(f"Creating app config folder")
        os.makedirs(cfg_dir)

    logger.debug(f"KemistDb paths:")
    logger.debug(f"Config : {cfg_dir}")
    logger.debug(f"Data : {data_dir}")

    return data_dir, cfg_dir


class ConfigManager(object):
    def __init__(self):
        self.data_dir, self.cfg_dir = get_app_dirs()
        self.config_file = os.path.join(self.cfg_dir, 'config.ini')

        config = configparser.ConfigParser()
        if not config.read(self.config_file):
            logger.info(f"No configuration folder found. Setting up default values")
            self.default_database = None
            self.databases = []
        else:
            self.default_database = config['SETTINGS']['default_database']
            self.databases = json.loads(config['SETTINGS']['databases'])
            logger.debug(f"Settings : {config['SETTINGS']}")

    def get_default_database_name(self):
        return self.default_database

    def get_default_database_path(self):
        return os.path.join(self.data_dir, self.default_database) if self.default_database else None

    def get_database_path(self, name):
        if name not in self.databases:
            logger.error(f"{name} is not a known database.")
            logger.debug(f"Known databases are {self.databases}")
            raise RuntimeError(f"{name} is not a known database. Known databases are {self.databases}")
        return os.path.join(self.data_dir, name)

    def set_default_database(self, name):
        if name in self.databases:
            self.default_database = name
            logger.info(f"Set {name} as the default database")
        else:
            logger.error(f"{name} is not a known database.")
            logger.debug(f"Known databases are {self.databases}")
            raise RuntimeError(f"{name} is not a known database. Known databases are {self.databases}")

    def register_database(self, name, set_as_default=False):
        if name in self.databases:
            logger.error(f"{name} is already a registered database.")
            raise RuntimeError(f"{name} is already a registered database.")

        self.databases.append(name)
        logger.info(f"Registered new database: {name}")

        if set_as_default or len(self.databases) == 1:
            self.set_default_database(name)
        return self.get_database_path(name)

    def clean_databases(self):
        to_keep = []
        for name in self.databases:
            if os.path.exists(self.get_database_path(name)):
                to_keep.append(name)
        self.databases = to_keep

        if self.default_database not in self.databases:
            self.default_database = self.databases[0] if len(self.databases) > 0 else None

    def save(self):
        logger.info(f"Saving configuration")
        config = configparser.ConfigParser()
        config['SETTINGS'] = {
            'default_database': self.default_database,
            'databases': f"{json.dumps(self.databases)}"
        }
        with open(self.config_file, 'w') as configfile:
            config.write(configfile)
