import unittest
import sys
import os

# Allows importing model.py from the parent folder
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from model import Breadboard, Breadboard


class TestBreadboardTopology(unittest.TestCase):

    def setUp(self):
        # setUp runs before EVERY test method — gives each test a fresh board
        self.board = Breadboard()

    def test_same_row_same_side_connected(self):
        h1 = ("main", 12, "a")
        h2 = ("main", 12, "c")
        self.assertTrue(self.board.are_connected(h1, h2))

    def test_same_row_opposite_sides_not_connected(self):
        h1 = ("main", 12, "a")
        h2 = ("main", 12, "f")
        self.assertFalse(self.board.are_connected(h1, h2))

    def test_different_rows_not_connected(self):
        h1 = ("main", 12, "c")
        h2 = ("main", 13, "c")
        self.assertFalse(self.board.are_connected(h1, h2))

    def test_power_rail_full_length_connected(self):
        h1 = ("top_rail", "+", 1)
        h2 = ("top_rail", "+", 40)
        self.assertTrue(self.board.are_connected(h1, h2))

    def test_top_rail_positive_and_negative_separate(self):
        h1 = ("top_rail", "+", 1)
        h2 = ("top_rail", "-", 1)
        self.assertFalse(self.board.are_connected(h1, h2))

    def test_top_and_bottom_rails_separate(self):
        h1 = ("top_rail", "+", 1)
        h2 = ("bottom_rail", "+", 1)
        self.assertFalse(self.board.are_connected(h1, h2))

    def test_unknown_hole_raises_error(self):
        h1 = ("main", 12, "a")
        h_fake = ("main", 999, "z")  # doesn't exist
        with self.assertRaises(ValueError):
            self.board.are_connected(h1, h_fake)

    def test_all_five_holes_in_group_mutually_connected(self):
        # every pair within a-e in the same row should be connected
        cols = ["a", "b", "c", "d", "e"]
        row = 5
        for i in range(len(cols)):
            for j in range(len(cols)):
                h1 = ("main", row, cols[i])
                h2 = ("main", row, cols[j])
                self.assertTrue(self.board.are_connected(h1, h2),
                    f"{h1} and {h2} should be connected")


if __name__ == "__main__":
    unittest.main()