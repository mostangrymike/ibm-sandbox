#!/usr/bin/env python3
"""Host-only crash and corruption checks for selector protocol."""
import unittest
from active_generation_selector import choose, decode, encode

OLD = "A" * 40
NEW = "B" * 40


class SelectorRecovery(unittest.TestCase):
    def setUp(self):
        self.old = encode(41, "GITOLD", OLD)
        self.new = encode(42, "GITNEW", NEW)
        self.accept = {("GITOLD", OLD), ("GITNEW", NEW)}
        self.checks = []

    def verify(self, name, digest):
        self.checks.append((name, digest))
        return (name, digest) in self.accept

    def test_both_complete(self):
        self.assertEqual(choose(self.old, self.new, self.verify),
                         (42, "GITNEW", NEW))

    def test_interrupted_new_slot(self):
        for size in range(len(self.new)):
            truncated = self.new[:size]
            self.assertEqual(
                choose(self.old, truncated, self.verify),
                (41, "GITOLD", OLD),
                msg=f"truncated new selector at byte {size}",
            )

    def test_new_candidate_fails_full_check(self):
        self.accept.remove(("GITNEW", NEW))
        self.assertEqual(choose(self.old, self.new, self.verify),
                         (41, "GITOLD", OLD))
        self.assertIn(("GITNEW", NEW), self.checks)

    def test_old_candidate_fails_full_check(self):
        self.accept.remove(("GITOLD", OLD))
        self.assertEqual(choose(self.old, self.new, self.verify),
                         (42, "GITNEW", NEW))

    def test_no_trusted_generation(self):
        self.accept.clear()
        self.assertIsNone(choose(self.old, self.new, self.verify))

    def test_changed_slot_checksum(self):
        bad = self.new.replace("GITNEW", "GITBAD")
        self.assertIsNone(decode(bad))
        self.assertEqual(choose(self.old, bad, self.verify),
                         (41, "GITOLD", OLD))

    def test_conflicting_same_sequence(self):
        conflicting = encode(41, "GITNEW", NEW)
        self.assertIsNone(choose(self.old, conflicting, self.verify))

    def test_identical_duplicate_slots(self):
        self.assertEqual(choose(self.old, self.old, self.verify),
                         (41, "GITOLD", OLD))

    def test_missing_slots(self):
        self.assertIsNone(choose("", "", self.verify))

    def test_strict_grammar(self):
        with self.assertRaises(ValueError):
            encode(0, "GITNEW", NEW)
        with self.assertRaises(ValueError):
            encode(2**32, "GITNEW", NEW)
        with self.assertRaises(ValueError):
            encode(42, "TOOLONGNAME", NEW)
        with self.assertRaises(ValueError):
            encode(42, "gitnew", NEW)
        with self.assertRaises(ValueError):
            encode(42, "GITNEW", "Z"*40)
        self.assertIsNone(decode(self.old + "garbage"))
        self.assertIsNone(decode(self.old + self.new))
        self.assertIsNone(decode(self.old.strip()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
