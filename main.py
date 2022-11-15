import kemist as km


def main(path, db):
    dbm = km.database.DatabaseManager(db)
    dbm.make_database()

    with open(path, encoding='utf-8') as input_file:
        csv_molecules = km.database.load_molecules(input_file)
        db_molecules = dbm.get_molecules()

        for molecule in csv_molecules:
            found = False

            for db_molecule in db_molecules:
                if km.core.are_same_molecules(molecule, db_molecule):
                    found = True
                    db_molecule.merge_with(molecule)
                    break

            if not found:
                db_molecules.append(molecule)

        # db_molecules should now contain the complete and reduced molecules list
        dbm.save_molecules(db_molecules)


if __name__ == '__main__':
    main("Database.csv", "test.sqlite3")
