import kemist as km


def _confirm(s):
    answer = ""
    while answer not in ["y", "n"]:
        answer = input(s).lower()
    return answer == "y"


def main(path, db, build):
    dbm = km.database.DatabaseManager(db)
    if build:
        dbm.make_database()

    with open(path, encoding='utf-8') as input_file:
        csv_molecules = km.database.load_molecules(input_file)
        db_molecules = dbm.get_molecules()

        found = False

        for molecule in csv_molecules:
            exact, potential, non = km.core.find_matching_molecules(molecule, db_molecules)
            for candidate in exact:
                candidate.merge_with(molecule)
                found = True
                break

            for candidate in potential:
                if _confirm(f"Are {candidate.known_names[0]} and {molecule.known_names[0]} the same molecule? "):
                    candidate.merge_with(molecule)
                    found = True
                    break

            db_molecules = exact + potential + non
            if not found:
                db_molecules.append(molecule)

        # db_molecules should now contain the complete and reduced molecules list
        for m in db_molecules:
            m.try_to_complete()

        dbm.save_molecules(db_molecules)


if __name__ == '__main__':
    main("db1.csv", "test.sqlite3", True)
    print("Second file")
    main("db2.csv", "test.sqlite3", False)
