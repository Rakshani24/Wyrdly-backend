import unittest
import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from model import Breadboard
from wiring import NetlistBuilder
from components import Resistor, Battery
from comparision import compare_netlists


class TestVoltageDivider(unittest.TestCase):

    def test_correctly_wired_voltage_divider_matches(self):
        board = Breadboard()
        netlist = NetlistBuilder(board)

        battery = Battery("BAT1", ("main", 3, "a"), ("main", 20, "a"), voltage=9.0)
        r1 = Resistor("R1", ("main", 3, "b"), ("main", 12, "a"), resistance_ohms=1000)
        r2 = Resistor("R2", ("main", 12, "b"), ("main", 20, "b"), resistance_ohms=1000)

        netlist.add_component(battery)
        netlist.add_component(r1)
        netlist.add_component(r2)

        user_result = netlist.build_netlist()

        ref_path = os.path.join(os.path.dirname(__file__), '..', 'reference_circuits', 'voltage_divider.json')
        with open(ref_path) as f:
            reference = json.load(f)

        report = compare_netlists(user_result, reference["expected_nets"])

        self.assertTrue(report["correct"])
        self.assertEqual(len(report["missing_nets"]), 0)
        self.assertEqual(len(report["extra_nets"]), 0)


if __name__ == "__main__":
    unittest.main()