import appdirs
import configparser
import os
import sqlite3

from .request_adapters import make_database_structure

import kemist.core as km


def get_app_dirs(app_name):
    data_dir = os.path.join(appdirs.user_data_dir(app_name), "databases")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    cfg_dir = appdirs.user_config_dir(app_name)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    return data_dir, cfg_dir


class KemistDbManager(object):
    def __init__(self, name):
        self.data_dir, self.cfg_dir = get_app_dirs(name)
        self.config_file = os.path.join(self.cfg_dir, 'config.ini')

        km.logger.debug(f"Configuration folder: {self.cfg_dir}")
        km.logger.debug(f"Database storage folder: {self.data_dir}")

    def get_default_database_name(self):
        if not os.path.exists(self.config_file):
            km.logger.debug(f"{self.config_file} not found")
            km.logger.warn(f"Config file not found. This is likely because no database was created yet")
            return None

        config = configparser.ConfigParser()
        config.read(self.config_file)
        return config['SETTINGS']['default_database']

    def get_database_names(self):
        databases = os.listdir(self.data_dir)
        km.logger.debug(f"Existing files in {self.data_dir}:\n {databases}")
        return databases

    def set_default_database(self, name):
        if name in self.get_database_names():
            config = configparser.ConfigParser()
            config['SETTINGS'] = {'default_database': name}
            with open(self.config_file, 'w') as configfile:
                config.write(configfile)
                km.logger.info(f"{name} is now the default database")
                return True

        km.logger.error(f"{name} is not an existing database name")
        return False

    def get_database_handle(self, name=None):
        if len(self.get_database_names()) == 0:
            if name is not None:
                self.set_default_database(name)
            else:
                km.logger.error(f"Default database handles require at least one database to exist")
                return None, None
        elif name is None:
            name = self.get_default_database_name()
            if name is None:
                km.logger.error(f"Default database is not set.")
                return None, None

        database_path = os.path.join(self.data_dir, name)
        already_exists = os.path.exists(self.database_path)

        connection = sqlite3.connect(database_path)
        cursor = self.connection.cursor()
        if not already_exists:
            km.logger.info(f"Creating database structure for {name}")
            make_database_structure(connection, cursor)

        return connection, cursor
