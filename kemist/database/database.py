import sqlite3

from kemist.core import Molecule, StorageUnit
from kemist.core import logger

import kemist.database.build_request as requests


class Database(object):
    def __init__(self, path):
        logger.debug(f"Connecting to {path}")
        self.connection = sqlite3.connect(path)
        self.cursor = self.connection.cursor()

    def _molecule_from_req(self, req, req_args):
        res = self.cursor.execute(req, req_args)
        molecules = [
            Molecule(uid, iupac, formula, on_libview, mode) for uid, iupac, formula, on_libview, mode in res.fetchall()
        ]

        for m in molecules:
            res = self.cursor.execute("SELECT name FROM molecule_names WHERE molecule_uid=?", [m.uid])
            for (name,) in res.fetchall():
                m.known_names.append(name)

            res = self.cursor.execute(
                "SELECT retention_time, column FROM molecule_retention_times WHERE molecule_uid=?", [m.uid]
            )

            for rt, column in res.fetchall():
                m.retention_times[column] = rt

        return molecules

    def make_structure(self):
        requests.make_database_structure(self.connection, self.cursor)

    def get_molecules(self):
        return self._molecule_from_req("SELECT uid, iupac, formula, in_libview, mode FROM molecules", [])

    def get_storage_units(self):
        storage_units = []

        res = self.cursor.execute("SELECT name FROM storage_units")
        for (name,) in res.fetchall():
            logger.debug(f"Fetching storage content for {name}")

            request = "SELECT uid, iupac, formula, in_libview, mode FROM molecules/n"
            request += "WHERE uid IN ("
            request += "SELECT molecule_uid FROM molecule_storage WHERE storage_name = ?"
            request += ")"

            stored_molecules = self._molecule_from_req(request, [name])

            storage_units.append(StorageUnit(name, stored_molecules))
        return storage_units

    def get_known_retention_times(self):
        res = self.cursor.execute("SELECT DISTINCT column FROM molecule_retention_times")
        names = []
        for (name,) in res.fetchall():
            names.append(name)

        return names

    def update_all_molecules(self, molecules):
        for m in molecules:
            if m.uid is None:
                self._add_molecule(m)
            else:
                self._update_molecule(m)
        self.connection.commit()

    def update_all_storage_units(self, storage_units):
        for s in storage_units:
            self.cursor.execute("INSERT OR IGNORE INTO storage_units (name) VALUES(?)", [s.name])
            for m in s.molecules:
                if m.uid is None:
                    logger.error(f"Can't add an unknow molecule to storage. Skipping {m.known_names[0]}...")
                    continue

                self.cursor.execute(
                    "INSERT OR IGNORE INTO molecule_storage (molecule_uid, storage_name) VALUES(?, ?)", [m.uid, s.name]
                )

        self.connection.commit()

    def _add_molecule(self, m: Molecule):
        if m.uid is not None:
            logger.error(f"{m.known_names[0]} already exists in database (uid: {m.uid}). Skipping it")
            return

        self.cursor.execute(
            "INSERT INTO molecules (iupac, formula, in_libview, mode) VALUES(?, ?, ?, ?)",
            [m.iupac, m.formula, m.is_on_libview, m.mode],
        )
        m.uid = self.cursor.lastrowid

        for name in m.known_names:
            self.cursor.execute("INSERT INTO molecule_names (name, molecule_uid) VALUES(?, ?)", [name, m.uid])

        for column, value in m.retention_times.items():
            self.cursor.execute(
                "INSERT INTO molecule_retention_times (molecule_uid, column, retention_time) VALUES(?, ?, ?)",
                [m.uid, column, value],
            )
        return m

    def _update_molecule(self, m: Molecule):
        if m.uid is None:
            logger.error(f"{m.known_names[0]} does not exist in database. Skipping it")
            return

        for name in m.known_names:
            self.cursor.execute("INSERT OR IGNORE INTO molecule_names (name, molecule_uid) VALUES(?, ?)", [name, m.uid])
        for column, value in m.retention_times.items():
            self.cursor.execute(
                "INSERT OR IGNORE INTO molecule_retention_times (molecule_uid, column, retention_time) VALUES(?, ?, ?)",
                [m.uid, column, value],
            )

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

            if m.mode is not None:
                if m.iupac is not None or m.formula is not None or m.is_on_libview is not None:
                    req += ", "
                req += "mode=?"
                request_args.append(m.mode)

            req += " WHERE uid=?"
            request_args.append(m.uid)
            self.cursor.execute(req, request_args)
