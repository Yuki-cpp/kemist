import kemist.core as km
import kemist.config
import kemist.database

import kemist.apps as kapps


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
            res += f"{mol.iupac};" if mol.iupac is not None else ";"
            res += f"{mol.formula};" if mol.formula is not None else ";"
            res += f"yes;" if mol.is_on_libview == 1 else "no;"
            res += f"{mol.mode}" if mol.mode is not None else ""

            for retention_time in rts:
                res += f"; {mol.retention_times.get(retention_time, '')}"

            return res

        rt_names = database.get_known_retention_times()

        with open(dest, "w") as output:
            output.write("Name; IUPAC name; Formula; MSMS Library view; Mode")
            for rt in rt_names:
                output.write(";" + rt)
            output.write("\n")

            for m in database.get_molecules():
                output.write(as_str(m, rt_names) + "\n")

    def create(self, name, new_molecules, storage_units, should_complete_molecules, make_default):
        db_path = self.config.register_database(name, make_default)
        if db_path is None:
            return

        database = kemist.database.Database(db_path)
        database.make_structure()

        existing_molecules = []
        KemistDb._merge_in_existing_molecule_list(new_molecules, existing_molecules, should_complete_molecules)
        database.update_all_molecules(existing_molecules)

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

    @staticmethod
    def _merge_in_existing_molecule_list(new_molecules, existing_molecules, should_complete_molecules):
        for new_molecule in new_molecules:
            if should_complete_molecules:
                new_molecule.try_to_complete()

            for existing_molecule in existing_molecules:
                equi = km.are_same_molecules(new_molecule, existing_molecule)
                if equi == km.Equivalence.STRICT:
                    existing_molecules.merge_with(new_molecule)
                    found = True
                elif equi == km.Equivalence.RELAXED:
                    if kapps.confirm(
                        f"Are {new_molecule.known_names[0]}"
                        " the same molecule as {existing_molecules.known_names[0]}? "
                        "[y/n]\n"
                    ):
                        existing_molecules.merge_with(new_molecule)
                        found = True
            if not found:
                existing_molecules.append(new_molecule)

    def update(self, name, new_molecules, new_storage_units, should_complete_molecules):
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

        if new_molecules:
            existing_molecules = database.get_molecules()
            KemistDb._merge_in_existing_molecule_list(new_molecules, existing_molecules, should_complete_molecules)
            database.update_all_molecules(existing_molecules)

        if new_storage_units:
            existing_storage_units = database.get_storage_units()
            existing_molecules = database.get_molecules()

            for new_unit in new_storage_units:
                for m in new_unit.molecules:
                    for existing_molecule in existing_molecules:
                        equi = km.are_same_molecules(m, existing_molecule)
                        if equi == km.Equivalence.STRICT:
                            m.merge_with(existing_molecule)
                            break

                found = False
                for existing_unit in existing_storage_units:
                    if new_unit.name == existing_unit.name:
                        existing_unit.molecules.extend(new_unit.molecules)
                        break

                if not found:
                    existing_storage_units.append(new_unit)

            database.update_all_storage_units(existing_storage_units)
