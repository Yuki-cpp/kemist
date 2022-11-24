import fuzzysearch

from kemist2.core import logger


def _are_name_close(a, b):
    tot = len(fuzzysearch.find_near_matches(a, b, max_l_dist=1)) + len(
        fuzzysearch.find_near_matches(b, a, max_l_dist=1))
    return tot > 0


class Molecule(object):
    def __init__(self, uid=None, iupac=None, formula=None, is_on_libview=None, mode=None, known_names=None,
                 retention_times=None):
        self.uid = uid
        self.iupac = iupac
        self.formula = formula
        self.is_on_libview = is_on_libview
        self.mode = mode
        self.known_names = known_names if known_names is not None else []
        self.retention_times = retention_times if retention_times is not None else {}

    def merge_with(self, other):
        if self.uid is None:
            self.uid = other.uid
        if self.iupac is None:
            self.iupac = other.iupac
        if self.formula is None:
            self.formula = other.formula
        if self.is_on_libview is None:
            self.is_on_libview = other.is_on_libview
        if self.mode is None:
            self.mode = other.mode

        self.known_names.extend(name for name in other.known_names if name not in self.known_names)
        for key, value in other.retention_times.items():
            self.retention_times[key] = value


def are_same_molecules(m1: Molecule, m2: Molecule, strict=False):
    if m1.uid is not None and m2.uid is not None:
        return m1.uid == m2.uid

    if m1.iupac is not None and m2.iupac is not None:
        return m1.iupac == m2.iupac

    if m1.formula is not None and m2.formula is not None:
        return m1.formula == m2.formula

    if any(name in m2.known_names for name in m1.known_names):
        return True

    if not strict:
        logger.debug("Looking for a non strict match")
        for name1 in m1.known_names:
            for name2 in m2.known_names:
                if _are_name_close(name1, name2):
                    return True
    return False
