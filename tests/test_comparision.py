import unittest
import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from model import Breadboard
from wiring import NetlistBuilder
from components import Resistor, LED, Battery
from comparision import compare_netlists


class TestComparison(unittest.TestCase):

    def build_correct_circuit(self):
        board = Breadboard()
        netlist = NetlistBuilder(board)
        battery = Battery("BAT1", ("main", 5, "a"), ("main", 15, "a"), voltage=5.0)
        r1 = Resistor("R1", ("main", 5, "b"), ("main", 10, "a"), resistance_ohms=220)
        led1 = LED("LED1", ("main", 10, "b"), ("main", 15, "b"))
        netlist.add_component(battery)
        netlist.add_component(r1)
        netlist.add_component(led1)
        return netlist.build_netlist()

    def load_reference(self):
        path = os.path.join(os.path.dirname(__file__), '..', 'reference_circuits', 'led_resistor.json')
        with open(path) as f:
            return json.load(f)

    def test_correct_circuit_matches(self):
        user_result = self.build_correct_circuit()
        reference = self.load_reference()
        report = compare_netlists(user_result, reference["expected_nets"])
        self.assertTrue(report["correct"])
        self.assertEqual(len(report["missing_nets"]), 0)
        self.assertEqual(len(report["extra_nets"]), 0)

    def test_reversed_led_is_detected(self):
        board = Breadboard()
        netlist = NetlistBuilder(board)
        battery = Battery("BAT1", ("main", 5, "a"), ("main", 15, "a"), voltage=5.0)
        r1 = Resistor("R1", ("main", 5, "b"), ("main", 10, "a"), resistance_ohms=220)
        # anode/cathode swapped on purpose
        led1 = LED("LED1", ("main", 15, "b"), ("main", 10, "b"))
        netlist.add_component(battery)
        netlist.add_component(r1)
        netlist.add_component(led1)
        user_result = netlist.build_netlist()

        reference = self.load_reference()
        report = compare_netlists(user_result, reference["expected_nets"])

        self.assertFalse(report["correct"])
        self.assertTrue(len(report["missing_nets"]) > 0)
        self.assertTrue(len(report["extra_nets"]) > 0)


if __name__ == "__main__":
    unittest.main()