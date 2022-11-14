import fuzzysearch


def _confirm(s):
    answer = ""
    while answer not in ["y", "n"]:
        answer = input(s).lower()
    return answer == "y"


def _are_name_close(a, b):
    tot = len(fuzzysearch.find_near_matches(a, b, max_l_dist=1)) + len(
        fuzzysearch.find_near_matches(b, a, max_l_dist=1))
    return tot > 0


class Molecule(object):
    def __init__(self, uid=None, iupac=None, formula=None, is_on_libview=None, known_names=None, retention_times=None):
        self.uid = uid
        self.iupac = iupac
        self.formula = formula
        self.is_on_libview = is_on_libview
        self.known_names = known_names if known_names is not None else []
        self.retention_times = retention_times if retention_times is not None else []

    def merge_with(self, other):
        if self.uid is None:
            self.uid = other.uid
        if self.iupac is None:
            self.iupac = other.iupac
        if self.formula is None:
            self.formula = other.formula
        if self.is_on_libview is None:
            self.is_on_libview = other.is_on_libview

        self.known_names.extend(name for name in other.known_names if name not in self.known_names)
        self.retention_times.extend(name for name in other.retention_times if name not in self.retention_times)


def are_same_molecules(m1: Molecule, m2: Molecule):
    if m1.uid is not None and m1.uid == m2.uid or \
            m1.iupac is not None and m1.iupac == m2.iupac or \
            m1.formula is not None and m1.formula == m2.formula:
        return True

    for name1 in m1.known_names:
        for name2 in m2.known_names:
            if name1 == name2:
                return True
            elif _are_name_close(name1, name2):
                if _confirm(f"Is {name1} the same molecule as {name2}? [y/n]"):
                    return True
    return False
