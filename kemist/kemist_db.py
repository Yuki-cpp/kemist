import argparse
import logging
import appdirs
import configparser
import os
from os.path import exists

import kemist.database as kdb

logger = logging.getLogger("kemist")
logging.basicConfig()


def _load_app_dirs():
    data_dir = os.path.join(appdirs.user_data_dir("kemist"), "databases")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    cfg_dir = appdirs.user_config_dir("kemist")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    return data_dir, cfg_dir


def create(args):
    data_dir, config_dir = _load_app_dirs()
    db_path = os.path.join(data_dir, args.dest)

    logger.debug(f"create : {db_path} - {args.molecules} - {args.storage} - {args.complete}")

    if exists(db_path):
        logger.error(f"Invalid input, {args.dest} already exists.")
        return

    logger.info(f"Creating database : {args.dest}")
    dbm = kdb.DatabaseManager(db_path)
    dbm.make_database()

    if args.molecules:
        logger.info(f"Adding molecules to database")

        csv_molecules = kdb.load_molecules(args.molecules)
        if args.complete:
            logger.info(f"Updating molecules informations")
            for m in csv_molecules:
                m.try_to_complete(logger=logger.debug)

        logger.info(f"Adding storage information to database")

    dbm.update_all_molecules(csv_molecules)

    if args.make_default or len(os.listdir(data_dir)) == 1:
        logger.info(f"Setting {args.dest} as default database")
        config = configparser.ConfigParser()
        config['DEFAULTS'] = {'database_path': db_path}
        with open(os.path.join(config_dir, 'config.ini'), 'w') as configfile:
            config.write(configfile)


def update(args):
    pass


def complete(args):
    pass


def export(args):
    data_dir, config_dir = _load_app_dirs()

    if args.name is not None:
        known_databases = os.listdir(data_dir)
        if args.name not in known_databases:
            logger.error(f"{args.name} is not a valid database name")
            return
        db_path = os.path.join(data_dir, args.name)
    else:
        config = configparser.ConfigParser()
        config.read(os.path.join(config_dir, 'config.ini'))
        db_path = config['DEFAULTS']['database_path']

    dbm = kdb.DatabaseManager(db_path)

    def as_str(mol, rts):
        res = f"{mol.known_names[0]};"
        res += f"{mol.iupac};" if mol.iupac is not None else ';'
        res += f"{mol.formula};" if mol.formula is not None else ';'
        res += f"yes;" if mol.is_on_libview == 1 else 'no;'
        res += f"{mol.mode}" if mol.mode is not None else ''

        for rt in rts:
            res += f"; {mol.retention_times.get(rt, '')}"

        return res

    rt_names = dbm.get_known_retention_times()

    with open(args.out, 'w') as output:
        output.write("Name; IUPAC name; Formula; MSMS Library view; Mode")
        for rt in rt_names:
            output.write(";" + rt)
        output.write("\n")
        
        for m in dbm.get_molecules():
            output.write(as_str(m, rt_names) + "\n")


def set_default(args):
    data_dir, config_dir = _load_app_dirs()

    known_databases = os.listdir(data_dir)
    if args.name not in known_databases:
        logger.error(f"{args.name} is not a valid database name")
        return

    logger.info(f"Setting {args.name} as default database")
    config = configparser.ConfigParser()
    config['DEFAULTS'] = {'database_path': os.path.join(data_dir, args.name)}
    with open(os.path.join(config_dir, 'config.ini'), 'w') as configfile:
        config.write(configfile)


def list_databases(_):
    data_dir, _ = _load_app_dirs()
    res = []
    for path in os.listdir(data_dir):
        if os.path.isfile(os.path.join(data_dir, path)):
            res.append(path)

    logger.info(f"Existing databases are :\n{res}")


def kemist_db():
    parser = argparse.ArgumentParser(
        prog='kemist-db',
        description='Database management tool for Kemist',
        epilog="Plz Gib Mony :'(")

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Print debug info'
    )

    subparsers = parser.add_subparsers(dest='verb')
    parser_create = subparsers.add_parser('create', help='Create a new database')
    parser_create.add_argument('dest', help='Database name')

    parser_create.add_argument(
        "-m",
        "--molecules",
        help="CSV input file for the list of molecules. If not specified, database will be left empty",
        type=argparse.FileType("r"),
        required=False,
    )
    parser_create.add_argument(
        "-s",
        "--storage",
        help="CSV input file for the molecule storage. Must be used with --molecules",
        type=argparse.FileType("r"),
        required=False,
    )
    parser_create.add_argument(
        '-c', '--complete',
        action='store_true',
        help='If set, will try to complete the molecules list using CIR'
    )
    parser_create.add_argument(
        '--make-default',
        action='store_true',
        help='If set, this database will become the default one.'
    )
    parser_create.set_defaults(func=create)

    parser_update = subparsers.add_parser('update', help='Update an existing database')
    parser_update.set_defaults(func=update)

    parser_complete = subparsers.add_parser('complete', help='Try to complete fields of an existing database')
    parser_complete.set_defaults(func=complete)

    parser_export = subparsers.add_parser('export', help='Export a database as a CSV file')
    parser_export.add_argument('out', help='Output file')
    parser_export.add_argument('--name', help='Database to export', required=False, default=None)
    parser_export.set_defaults(func=export)

    parser_set_default = subparsers.add_parser('set', help='Select the default database')
    parser_set_default.add_argument('name', help='Database name to set as default')
    parser_set_default.set_defaults(func=set_default)

    parser_list = subparsers.add_parser('list', help='List existing databases')
    parser_list.set_defaults(func=list_databases)

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    if args.verb:
        args.func(args)


if __name__ == '__main__':
    kemist_db()
