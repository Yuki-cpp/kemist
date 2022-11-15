import sqlite3
import kemist.core as km


class DatabaseManager(object):
    def __init__(self, db_path):
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()

    def make_database(self):
        # Drop all
        self.cursor.executescript('''
            DROP TRIGGER IF EXISTS "clear_storage_units_deps";
            DROP TRIGGER IF EXISTS "clear_molecules_deps";
            DROP TABLE IF EXISTS "molecule_storage";
            DROP TABLE IF EXISTS "storage_units";
            DROP TABLE IF EXISTS "molecule_retention_times";
            DROP TABLE IF EXISTS "molecule_names";
            DROP TABLE IF EXISTS "molecules";
        ''')

        # Create "main" tables
        self.cursor.executescript('''
            CREATE TABLE IF NOT EXISTS "molecules" (
                "uid"	INTEGER NOT NULL UNIQUE,
                "iupac"	TEXT UNIQUE,
                "formula"	TEXT UNIQUE,
                "in_libview"	INTEGER,
                PRIMARY KEY("uid" AUTOINCREMENT)
            );
            CREATE TABLE IF NOT EXISTS "storage_units" (
                "name"	TEXT NOT NULL UNIQUE,
                PRIMARY KEY("name")
            );
        ''')

        # Create other tables
        self.cursor.executescript('''
            CREATE TABLE IF NOT EXISTS "molecule_names" (
                "name"	TEXT NOT NULL,
                "molecule_uid"	INTEGER NOT NULL,
                FOREIGN KEY("molecule_uid") REFERENCES "molecules"("uid"),
                PRIMARY KEY("name")
            );
            CREATE TABLE "molecule_retention_times" (
                "molecule_uid"	INTEGER NOT NULL,
                "retention_time"	REAL NOT NULL,
                FOREIGN KEY("molecule_uid") REFERENCES "molecules"("uid"),
                PRIMARY KEY("molecule_uid","retention_time")
            );
            CREATE TABLE IF NOT EXISTS "molecule_storage" (
                "molecule_uid"	INTEGER NOT NULL,
                "storage_name"	TEXT NOT NULL,
                FOREIGN KEY("molecule_uid") REFERENCES "molecules"("uid"),
                FOREIGN KEY("storage_name") REFERENCES "storage_units"("name")
            );
        ''')

        # Create triggers
        self.cursor.executescript('''
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

        self.connection.commit()

    def get_molecules(self):
        res = self.cursor.execute("SELECT uid, iupac, formula, in_libview FROM molecules")
        molecules = [km.Molecule(uid, iupac, formula, on_libview) for uid, iupac, formula, on_libview in
                     res.fetchall()]

        for m in molecules:
            res = self.cursor.execute("SELECT name FROM molecule_names WHERE molecule_uid=?", [m.uid])
            m.known_names.extend(res.fetchall())
            res = self.cursor.execute("SELECT retention_time FROM molecule_retention_times WHERE molecule_uid=?",
                                      [m.uid])
            m.retention_times.extend(res.fetchall())

        return molecules

    def update_molecule(self, m: km.Molecule):
        if m.uid is None:
            # TODO proper error
            raise RuntimeError("Does not exist in database. Use add_molecule instead")

        for name in m.known_names:
            self.cursor.execute("INSERT OR IGNORE INTO molecule_names (name, molecule_uid) VALUES(?, ?)",
                                [name, m.uid])
        for rt in m.retention_times:
            self.cursor.execute(
                "INSERT OR IGNORE INTO molecule_retention_times (molecule_uid, retention_time) VALUES(?, ?)",
                [m.uid, rt])

        if m.iupac is not None or m.formula is not None or m.is_on_libview is not None:
            req = "UPDATE molecules SET "
            request_args = []

            if m.iupac is not None:
                req += "iupac=?"
                request_args.append(m.iupac)

            if m.formula is not None:
                if m.iupac is not None:
                    req += ", "
                req += "formula=?"
                request_args.append(m.formula)

            if m.is_on_libview is not None:
                if m.iupac is not None or m.formula is not None:
                    req += ", "
                req += "in_libview=?"
                request_args.append(m.is_on_libview)

            req += " WHERE uid=?"
            request_args.append(m.uid)
            self.cursor.execute(req, request_args)

        self.connection.commit()

    def add_molecule(self, m: km.Molecule):
        if m.uid is not None:
            # TODO proper error
            raise RuntimeError("Already exist in database Use update_molecule instead")

        self.cursor.execute("INSERT INTO molecules (iupac, formula, in_libview) VALUES(?, ?, ?)",
                            [m.iupac, m.formula, m.is_on_libview])
        m.uid = self.cursor.lastrowid

        for name in m.known_names:
            self.cursor.execute("INSERT INTO molecule_names (name, molecule_uid) VALUES(?, ?)",
                                [name, m.uid])
        for rt in m.retention_times:
            self.cursor.execute(
                "INSERT INTO molecule_retention_times (molecule_uid, retention_time) VALUES(?, ?)",
                [m.uid, rt])

        self.connection.commit()
        return m

    def save_molecules(self, molecules):
        for m in molecules:
            if m.uid is None:
                self.add_molecule(m)
            else:
                self.update_molecule(m)
