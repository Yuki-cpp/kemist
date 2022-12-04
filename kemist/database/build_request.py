import kemist.core as km


def make_database_structure(connection, cursor):
    km.logger.debug(f"Creating new database...")

    km.logger.debug(f"Removing Triggers and Tables...")
    cursor.executescript(
        """
        DROP TRIGGER IF EXISTS "clear_storage_units_deps";
        DROP TRIGGER IF EXISTS "clear_molecules_deps";
        DROP TABLE IF EXISTS "molecule_storage";
        DROP TABLE IF EXISTS "storage_units";
        DROP TABLE IF EXISTS "molecule_retention_times";
        DROP TABLE IF EXISTS "molecule_names";
        DROP TABLE IF EXISTS "molecules";
    """
    )

    km.logger.debug(f"Creating molecules and storage Tables...")
    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS "molecules" (
            "uid"	INTEGER NOT NULL UNIQUE,
            "iupac"	TEXT,
            "formula"	TEXT,
            "in_libview"	INTEGER,
            "mode"	TEXT,
            PRIMARY KEY("uid" AUTOINCREMENT)
        );
        CREATE TABLE IF NOT EXISTS "storage_units" (
            "name"	TEXT NOT NULL UNIQUE,
            PRIMARY KEY("name")
        );
    """
    )

    km.logger.debug(f"Creating other Tables...")
    cursor.executescript(
        """
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
    """
    )
    km.logger.debug(f"Creating Triggers...")
    cursor.executescript(
        """
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
    """
    )

    km.logger.debug(f"Commiting transaction...")
    connection.commit()
