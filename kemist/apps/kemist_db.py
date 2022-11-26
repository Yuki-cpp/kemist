import argparse

import kemist.core as km
import kemist.config
import kemist.database

import kemist.apps as kapps


def _confirm(s):
    answer = ""
    while answer not in ["y", "n"]:
        answer = input(s).lower()
    return answer == "y"


class KemistDb(object):
    def __init__(self):
        self.config = kemist.config.ConfigManager()

    def set_default(self, name):
        try:
            self.config.set_default_database(name)
            self.config.save()
        except RuntimeError:
            pass

    def list_databases(self):
        km.logger.info(f"Existing databases are :\n{self.config.databases}")

    def export(self, name, dest):
        if name is None:
            name = self.config.get_default_database_name()
            if name is None:
                km.logger.error(f"No database found")
                return
            km.logger.info(f"Using default database {name}")

        path = self.config.get_database_path(name)
        if path is None:
            km.logger.error(f"Could not open database {name}")
            return

        database = kemist.database.Database(path)

        def as_str(mol, rts):
            res = f"{mol.known_names[0]};"
            res += f"{mol.iupac};" if mol.iupac is not None else ';'
            res += f"{mol.formula};" if mol.formula is not None else ';'
            res += f"yes;" if mol.is_on_libview == 1 else 'no;'
            res += f"{mol.mode}" if mol.mode is not None else ''

            for retention_time in rts:
                res += f"; {mol.retention_times.get(rt, '')}"

            return res

        rt_names = database.get_known_retention_times()

        with open(dest, 'w') as output:
            output.write("Name; IUPAC name; Formula; MSMS Library view; Mode")
            for rt in rt_names:
                output.write(";" + rt)
            output.write("\n")

            for m in database.get_molecules():
                output.write(as_str(m, rt_names) + "\n")

    def create(self, name, molecules_input_file, storage_input_fine, should_complete_molecules, make_default):
        db_path = self.config.register_database(name, make_default)
        if db_path is None:
            return

        database = kemist.database.Database(db_path)
        database.make_structure()

        if molecules_input_file is not None:
            molecules = kapps.load_molecules(molecules_input_file)
        else:
            molecules = []

        final_molecules = []
        for molecule in molecules:
            found = False

            if should_complete_molecules:
                molecule.try_to_complete()

            for db_mol in final_molecules:
                equi = km.are_same_molecules(molecule, db_mol)
                if equi == km.Equivalence.STRICT:
                    db_mol.merge_with(molecule)
                    found = True
                elif equi == km.Equivalence.RELAXED:
                    if _confirm(f"Are {molecule.known_names[0]} the same molecule as {db_mol.known_names[0]}"):
                        db_mol.merge_with(molecule)
                        found = True
            if not found:
                final_molecules.append(molecule)
        database.update_all_molecules(final_molecules)

        if storage_input_fine is not None:
            storage_units = kapps.load_storage_areas(storage_input_fine)
        else:
            storage_units = []

        db_molecules = database.get_molecules()
        for su in storage_units:
            for m in su.molecules:
                for db_mol in db_molecules:
                    equi = km.are_same_molecules(m, db_mol)
                    if equi == km.Equivalence.STRICT:
                        m.merge_with(db_mol)
                        break

        database.update_all_storage_units(storage_units)

        self.config.save()


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

    parser_set_default = subparsers.add_parser('set', help='Select the default database')
    parser_set_default.add_argument('name', help='Database name to set as default')

    subparsers.add_parser('list', help='List existing databases')

    parser_export = subparsers.add_parser('export', help='Export a database as a CSV file')
    parser_export.add_argument('dest', help='Output file')
    parser_export.add_argument('--name', help='Database to export', required=False, default=None)

    args = parser.parse_args()

    km.set_verbose_logging(args.verbose)

    kemist_core = KemistDb()

    if args.verb == "create":
        kemist_core.create(args.dest, args.molecules, args.storage, args.complete, args.make_default)
    elif args.verb == "set":
        kemist_core.set_default(args.name)
    elif args.verb == "list":
        kemist_core.list_databases()
    elif args.verb == "export":
        kemist_core.export(args.name, args.dest)


if __name__ == '__main__':
    kemist_db()
