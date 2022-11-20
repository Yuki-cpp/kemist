import argparse
import logging
from os.path import exists

import kemist.database as kdb

logger = logging.getLogger("kemist")
logging.basicConfig()


def create(args):
    logger.debug(f"create : {args.dest} - {args.molecules} - {args.storage} - {args.complete}")

    if exists(args.dest):
        logger.error(f"Invalid input, {args.dest} already exists.")
        return

    logger.info(f"Creating database : {args.dest}")
    dbm = kdb.DatabaseManager(args.dest)
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


def update(args):
    pass


def complete(args):
    pass


def export(args):
    pass


def set_default(args):
    pass


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
    parser_create.add_argument('dest', help='Database output file')

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

    parser_create.set_defaults(func=create)

    parser_update = subparsers.add_parser('update', help='Update an existing database')
    parser_update.set_defaults(func=update)

    parser_complete = subparsers.add_parser('complete', help='Try to complete fields of an existing database')
    parser_complete.set_defaults(func=complete)

    parser_export = subparsers.add_parser('export', help='Export a database as a CSV file')
    parser_export.set_defaults(func=export)

    parser_set_default = subparsers.add_parser('set', help='Select the default database')
    parser_set_default.set_defaults(func=set_default)

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    if args.verb:
        args.func(args)


if __name__ == '__main__':
    kemist_db()
