BEGIN TRANSACTION;
DROP TABLE IF EXISTS "molecules";
CREATE TABLE IF NOT EXISTS "molecules" (
	"uid"	INTEGER NOT NULL UNIQUE,
	"iupac"	TEXT UNIQUE,
	"formula"	TEXT UNIQUE,
	"in_libview"	INTEGER,
	PRIMARY KEY("uid" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "molecule_names";
CREATE TABLE IF NOT EXISTS "molecule_names" (
	"name"	TEXT NOT NULL,
	"molecule_uid"	INTEGER NOT NULL,
	FOREIGN KEY("molecule_uid") REFERENCES "molecules"("uid"),
	PRIMARY KEY("name")
);
DROP TABLE IF EXISTS "molecule_retention_times";
CREATE TABLE IF NOT EXISTS "molecule_retention_times" (
	"molecule_uid"	INTEGER NOT NULL,
	"retention_time"	REAL NOT NULL,
	FOREIGN KEY("molecule_uid") REFERENCES "molecules"("uid")
);
DROP TABLE IF EXISTS "storage_units";
CREATE TABLE IF NOT EXISTS "storage_units" (
	"name"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("name")
);
DROP TABLE IF EXISTS "molecule_storage";
CREATE TABLE IF NOT EXISTS "molecule_storage" (
	"molecule_uid"	INTEGER NOT NULL,
	"storage_name"	TEXT NOT NULL,
	FOREIGN KEY("molecule_uid") REFERENCES "molecules"("uid"),
	FOREIGN KEY("storage_name") REFERENCES "storage_units"("name")
);
DROP TRIGGER IF EXISTS "clear_molecules_deps";
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
COMMIT;
