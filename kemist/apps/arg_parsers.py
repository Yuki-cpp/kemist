import argparse
from argformat import StructuredFormatter


def make_kemist_db_parser():
    parser = argparse.ArgumentParser(
        prog="kemist-db",
        description="Database management tool for Kemist",
        epilog="Plz Gib Mony :'(",
        formatter_class=StructuredFormatter,
    )

    subparsers = parser.add_subparsers(dest="verb")
    parser_create = subparsers.add_parser(
        "create",
        description="Create a new Kemist database",
        help="create a new database.",
        formatter_class=StructuredFormatter,
    )
    parser_create.add_argument(
        "database",
        help="name of the new database\n"
             "Database names must be unique (see the list command for a list of existing databases)",
    )

    parser_create.add_argument(
        "--make-default", action="store_true", help="set the database as default"
    )

    parser_update = subparsers.add_parser("update", help="Update an existing database",
                                          formatter_class=StructuredFormatter, )
    parser_update.add_argument("--database", help="Database to export", required=False, default=None)

    parser_set_default = subparsers.add_parser("set", help="Select the default database",
                                               formatter_class=StructuredFormatter, )
    parser_set_default.add_argument("database", help="Database name to set as default")

    parser_list = subparsers.add_parser("list", help="List existing databases", formatter_class=StructuredFormatter, )

    parser_export = subparsers.add_parser("export", help="Export a database as a CSV file",
                                          formatter_class=StructuredFormatter, )
    parser_export.add_argument("output", help="Output file")
    parser_export.add_argument("--database", help="Database to export", required=False, default=None)

    for p in [parser_create, parser_update, parser_set_default, parser_list, parser_export]:
        p.add_argument("-v", "--verbose", action="store_true", help="Enables verbose logging output.")

    for p in [parser_create, parser_update]:
        p.add_argument(
            "-m",
            "--molecules",
            help="molecules to add to the database\n"
                 "This must be the path to a CSV file containing the following header:\n"
                 "Name;IUPAC name;Formula;MSMS library view;Mode;RT 1;RT 2; ...; RT N\n"
                 "Only Name is mandatory and other cells can be left empty (but must still exist)\n"
                 "If this argument is ommited, no molecule will be added to the database\n ",
            type=argparse.FileType("r"),
            required=False,
        )
        p.add_argument(
            "-s",
            "--storage",
            help="storage information to add to the database\n"
                 "This must be the path to a CSV file containing the following header:\n"
                 "Name;Storage\n"
                 "Where Name contains a molecule name and Storage contains the name of a storage unit containing it\n"
                 "If this argument is ommited, no storage information will be added to the database\n ",
            type=argparse.FileType("r"),
            required=False,
        )
        p.add_argument(
            "-c",
            "--complete",
            action="store_true",
            help="complete molecules information using CIR."
        )

        group = p.add_mutually_exclusive_group()
        group.add_argument(
            "-S",
            "--strict",
            action="store_true",
            help="[Default] Strict use strict matching. " "Can't be used with -I nor -R",
        )
        group.add_argument(
            "-I",
            "--interactive",
            action="store_true",
            help="Strict use interactive matching. " "Can't be used with -S nor -R",
        )
        group.add_argument(
            "-R",
            "--relaxed",
            action="store_false",
            help="Strict use relaxed matching. " "Can't be used with -S nor -I",
        )

    return parser
