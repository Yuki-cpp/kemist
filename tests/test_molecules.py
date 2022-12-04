import unittest

import kemist.core as core


class MoleculesTest(unittest.TestCase):
    def test_is_list_of_strings(self):
        self.assertTrue(core.molecule._is_list_of_strings(["a", "b"]))
        self.assertFalse(core.molecule._is_list_of_strings([]))
        self.assertFalse(core.molecule._is_list_of_strings("abc"))
        self.assertFalse(core.molecule._is_list_of_strings({}))

    def test_merging(self):
        m1 = core.Molecule()
        self.assertIsNone(m1.uid)
        self.assertIsNone(m1.iupac)
        self.assertIsNone(m1.formula)
        self.assertIsNone(m1.is_on_libview)
        self.assertIsNone(m1.mode)
        self.assertEqual(len(m1.known_names), 0)
        self.assertEqual(m1.retention_times, {})

        m2 = core.Molecule(uid=1, formula="H2O", is_on_libview=True, known_names=["water", "dihydrogen oxide"])
        self.assertIsNotNone(m2.uid)
        self.assertEqual(m2.uid, 1)
        self.assertIsNotNone(m2.formula)
        self.assertEqual(m2.formula, "H2O")
        self.assertEqual(len(m2.known_names), 2)
        self.assertEqual(m2.known_names, ["water", "dihydrogen oxide"])
        self.assertIsNotNone(m2.is_on_libview)
        self.assertTrue(m2.is_on_libview)
        self.assertIsNone(m2.mode)
        self.assertIsNone(m2.iupac)
        self.assertEqual(m2.retention_times, {})

        m1.merge_with(m2)
        self.assertIsNotNone(m1.uid)
        self.assertEqual(m1.uid, 1)
        self.assertIsNotNone(m1.formula)
        self.assertEqual(m1.formula, "H2O")
        self.assertEqual(len(m1.known_names), 2)
        self.assertEqual(m1.known_names, ["water", "dihydrogen oxide"])
        self.assertIsNotNone(m1.is_on_libview)
        self.assertTrue(m1.is_on_libview)
        self.assertIsNone(m1.mode)
        self.assertIsNone(m1.iupac)
        self.assertEqual(m1.retention_times, {})

    def test_are_same_molecules(self):
        m1 = core.Molecule(uid=1, formula="H2O", iupac="WaTer", known_names=["water", "dihydrogen oxide"])
        m2 = core.Molecule()
        self.assertEqual(core.are_same_molecules(m1, m2), core.Equivalence.NONE)
        self.assertEqual(core.are_same_molecules(m2, m1), core.Equivalence.NONE)

        m1 = core.Molecule(uid=1, formula="H2O", iupac="WaTer", known_names=["water", "dihydrogen oxide"])
        m2 = core.Molecule(uid=1)
        self.assertEqual(core.are_same_molecules(m1, m2), core.Equivalence.STRICT)
        self.assertEqual(core.are_same_molecules(m2, m1), core.Equivalence.STRICT)

        m1 = core.Molecule(uid=1, iupac="Oil", formula="C12O9H5")
        m2 = core.Molecule(uid=1)
        self.assertEqual(core.are_same_molecules(m1, m2), core.Equivalence.STRICT)
        self.assertEqual(core.are_same_molecules(m2, m1), core.Equivalence.STRICT)

        m1 = core.Molecule(uid=1, formula="H2O", iupac="WaTer", known_names=["water", "dihydrogen oxide"])
        m2 = core.Molecule(uid=2, formula="H2O", iupac="WaTer", known_names=["water", "dihydrogen oxide"])
        self.assertEqual(core.are_same_molecules(m1, m2), core.Equivalence.NONE)
        self.assertEqual(core.are_same_molecules(m2, m1), core.Equivalence.NONE)

        m1 = core.Molecule(uid=1, formula="H2O", iupac="WaTer", known_names=["water", "dihydrogen oxide"])
        m2 = core.Molecule(known_names=["water", "dihydrogen oxide"])
        self.assertEqual(core.are_same_molecules(m1, m2), core.Equivalence.STRICT)
        self.assertEqual(core.are_same_molecules(m2, m1), core.Equivalence.STRICT)

        m1 = core.Molecule(uid=1, formula="H2O", iupac="WaTer", known_names=["water", "dihydrogen oxide"])
        m2 = core.Molecule(known_names=["waer"])
        self.assertEqual(core.are_same_molecules(m1, m2), core.Equivalence.RELAXED)
        self.assertEqual(core.are_same_molecules(m2, m1), core.Equivalence.RELAXED)


if __name__ == "__main__":
    unittest.main()
