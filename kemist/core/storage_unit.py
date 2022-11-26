import kemist.core as km


class StorageUnit(object):
    def __init__(self, name, molecules=None):
        self.name = name
        self.molecules = molecules if molecules is not None else []

    def add(self, molecule: km.Molecule):
        self.molecules.append(molecule)

    def contains(self, molecule: km.Molecule, strict=False):
        for m in self.molecules:
            if km.are_same_molecules(m, molecule, strict):
                km.logger.debug(f"{molecule.known_names[0]} was found in storage {self.name}")
                return True

        km.logger.debug(f"{molecule.known_names[0]} was not found in storage {self.name}")
        return False
