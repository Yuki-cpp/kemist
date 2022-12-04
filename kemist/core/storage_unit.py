import kemist.core as km


class StorageUnit(object):
    def __init__(self, name, molecules=None):
        self.name = name
        self.molecules = molecules if molecules is not None else []
