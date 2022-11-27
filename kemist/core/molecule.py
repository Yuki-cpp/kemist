import fuzzysearch
import cirpy
from enum import Enum
from kemist.core import logger


def _are_name_close(a, b):
    tot = len(fuzzysearch.find_near_matches(a, b, max_l_dist=1)) + len(
        fuzzysearch.find_near_matches(b, a, max_l_dist=1)
    )
    return tot > 0


def _is_list_of_strings(lst):
    return bool(lst) and not isinstance(lst, str) and all(isinstance(elem, str) for elem in lst)


class Molecule(object):
    def __init__(
            self, uid=None, iupac=None, formula=None, is_on_libview=None, mode=None, known_names=None,
            retention_times=None
    ):
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

    def try_to_complete(self):
        logger.info(f"Trying to complete {self.known_names[0]}")
        logger.debug(f"Current IUPAC : {self.iupac}")
        logger.debug(f"Current Formula : {self.formula}")

        if self.iupac is None:
            for n in self.known_names:
                self.iupac = cirpy.resolve(n, "iupac_name")
                if self.iupac is not None:
                    if _is_list_of_strings(self.iupac):
                        selected_iupac = self.iupac[0]
                        logger.warning(f"{self.known_names[0]} has an ambiguous IUPAC name.")
                        logger.warning(
                            f"Selecting {selected_iupac} and discarding the following ones: {self.iupac[1:]}..."
                        )
                        self.iupac = selected_iupac
                    break

        if self.iupac is None:
            logger.warning(f"Could not complete {self.known_names[0]}...")
            return

        if self.formula is None:
            self.formula = cirpy.resolve(self.iupac, "formula")


class Equivalence(Enum):
    STRICT = 1
    RELAXED = 2
    NONE = 3


def are_same_molecules(m1: Molecule, m2: Molecule):
    if m1.uid is not None and m2.uid is not None:
        return Equivalence.STRICT if m1.uid == m2.uid else Equivalence.NONE

    if m1.iupac is not None and m2.iupac is not None:
        return Equivalence.STRICT if m1.iupac == m2.iupac else Equivalence.NONE

    if m1.formula is not None and m2.formula is not None:
        return Equivalence.STRICT if m1.formula == m2.formula else Equivalence.NONE

    if any(name in m2.known_names for name in m1.known_names):
        return Equivalence.STRICT

    for name1 in m1.known_names:
        for name2 in m2.known_names:
            if _are_name_close(name1, name2):
                return Equivalence.RELAXED
    return Equivalence.NONE
