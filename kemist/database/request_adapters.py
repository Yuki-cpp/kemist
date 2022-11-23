import kemist.core as km


def make_database_structure(connection, cursor):
    km.logger.debug(f"Creating new database...")

    km.logger.debug(f"Removing Triggers and Tables...")
    cursor.executescript('''
        DROP TRIGGER IF EXISTS "clear_storage_units_deps";
        DROP TRIGGER IF EXISTS "clear_molecules_deps";
        DROP TABLE IF EXISTS "molecule_storage";
        DROP TABLE IF EXISTS "storage_units";
        DROP TABLE IF EXISTS "molecule_retention_times";
        DROP TABLE IF EXISTS "molecule_names";
        DROP TABLE IF EXISTS "molecules";
    ''')

    km.logger.debug(f"Creating molecules and storage Tables...")
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS "molecules" (
            "uid"	INTEGER NOT NULL UNIQUE,
            "iupac"	TEXT UNIQUE,
            "formula"	TEXT UNIQUE,
            "in_libview"	INTEGER,
            "mode"	TEXT,
            PRIMARY KEY("uid" AUTOINCREMENT)
        );
        CREATE TABLE IF NOT EXISTS "storage_units" (
            "name"	TEXT NOT NULL UNIQUE,
            PRIMARY KEY("name")
        );
    ''')

    km.logger.debug(f"Creating other Tables...")
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS "molecule_names" (
            "name"	TEXT NOT NULL,
            "molecule_uid"	INTEGER NOT NULL,
            FOREIGN KEY("molecule_uid") REFERENCES "molecules"("uid"),
            PRIMARY KEY("name")
        );
        CREATE TABLE "molecule_retention_times" (
            "molecule_uid"	INTEGER NOT NULL,
            "column"	TEXT NOT NULL,
            "retention_time"	REAL NOT NULL,
            FOREIGN KEY("molecule_uid") REFERENCES "molecules"("uid"),
            PRIMARY KEY("molecule_uid","column")
        );
        CREATE TABLE IF NOT EXISTS "molecule_storage" (
            "molecule_uid"	INTEGER NOT NULL,
            "storage_name"	TEXT NOT NULL,
            FOREIGN KEY("molecule_uid") REFERENCES "molecules"("uid"),
            FOREIGN KEY("storage_name") REFERENCES "storage_units"("name")
        );
    ''')

    km.logger.debug(f"Creating Triggers...")
    cursor.executescript('''
        CREATE TRIGGER clear_molecules_deps
            BEFORE DELETE
            ON molecules
        BEGIN
            DELETE FROM molecule_names WHERE molecule_uid=OLD.uid;
            DELETE FROM molecule_retention_times WHERE molecule_uid=OLD.uid;
            DELETE FROM molecule_storage WHERE molecule_uid=OLD.uid;
        END;
        DROP TRIGGER IF EXISTS "clear_storage_units_deps";
        CREATE TRIGGER clear_storage_units_deps
            BEFORE DELETE
            ON storage_units
        BEGIN
            DELETE FROM molecule_storage WHERE storage_name=OLD.name;
        END;            
    ''')

    km.logger.debug(f"Commiting transaction...")
    connection.commit()


def select_molecules(cursor):
    request = "SELECT uid, iupac, formula, in_libview, mode FROM molecules"
    km.logger.debug(f"Executing request:\n{request}")

    res = cursor.execute(request)
    molecules = [km.Molecule(uid, iupac, formula, on_libview, mode) for uid, iupac, formula, on_libview, mode in
                 res.fetchall()]
    return molecules


def select_molecule_known_names(cursor, molecule_uid):
    request = "SELECT name FROM molecule_names WHERE molecule_uid=?"
    km.logger.debug(f"Executing request:\n{request}")
    km.logger.debug(f"With the following args:\n{molecule_uid}")

    res = cursor.execute(request, [molecule_uid])
    names = []
    for name, in res.fetchall():
        names.append(name)
    return names


def select_molecule_retention_times(cursor, molecule_uid):
    request = "SELECT retention_time, column FROM molecule_retention_times WHERE molecule_uid=?"
    km.logger.debug(f"Executing request:\n{request}")
    km.logger.debug(f"With the following args:\n{molecule_uid}")

    res = cursor.execute(request, [molecule_uid])
    retention_times = {}
    for rt, column in res.fetchall():
        retention_times[column] = rt
    return retention_times


def select_existing_retention_times_categories(cursor):
    request = "SELECT DISTINCT column FROM molecule_retention_times"
    km.logger.debug(f"Executing request:\n{request}")

    res = cursor.execute(request)
    categories = []
    for category, in res.fetchall():
        categories.append(category)
    return res.fetchall()
