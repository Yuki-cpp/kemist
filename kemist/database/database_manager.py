import sqlite3
import kemist.core as km


class DatabaseManager(object):
    def __init__(self, db_path):
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()

    def get_molecules(self):
        res = self.cursor.execute("SELECT id, iupac, formula, onLibView FROM MoleculeNames")
        molecules = [km.Molecule(uid, iupac, formula, is_on_libview) for uid, iupac, formula, is_on_libview in
                     res.fetchall()]

        for m in molecules:
            res = self.cursor.execute("SELECT name FROM MoleculeNames WHERE moleculeId=?", [m.uid])
            m.known_names.extend(res.fetchall())

            res = self.cursor.execute("SELECT time FROM RetentionTimes WHERE moleculeId=?", [m.uid])
            m.retention_times.extend(res.fetchall())
        return m

    def add_molecule(self, m: km.Molecule):
        if m.uid is not None:
            # TODO proper error
            raise RuntimeError("Already exist in database")

        self.cursor.execute("INSERT INTO Molecules (iupac, formula, onLibView) VALUES(?, ?, ?)",
                            [m.iupac, m.formula, m.is_on_libview])
        m.uid = self.cursor.lastrowid

        for name in m.known_names:
            self.cursor.execute("INSERT INTO MoleculeNames (moleculeId, name) VALUES(?, ?)",
                                [m.uid, name])
        for rt in m.retention_times:
            self.cursor.execute("INSERT INTO RetentionTimes (moleculeId, time) VALUES(?, ?)",
                                [m.uid, rt])

        self.connection.commit()
        return m

    def update_molecules(self, molecules):
        for m in molecules:
            if m.uid is None:
                self.add_molecule(m)
            else:
                pass  # Need to update the molecule in the database
