import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from model import Breadboard
from wiring import NetlistBuilder
from components import Resistor, LED, Battery


class TestComponents(unittest.TestCase):

    def setUp(self):
        self.board = Breadboard()
        self.netlist = NetlistBuilder(self.board)

    def test_component_pins_land_in_correct_nets(self):
        r1 = Resistor("R1", ("main", 5, "a"), ("main", 10, "a"), resistance_ohms=220)
        self.netlist.add_component(r1)

        result = self.netlist.build_netlist()

        # R1's two pins should NOT be in the same net (component doesn't merge nets)
        net_names = list(result.keys())
        pin1_net = None
        pin2_net = None
        for net_root, pins in result.items():
            for comp_name, pin_name in pins:
                if comp_name == "R1" and pin_name == "pin1":
                    pin1_net = net_root
                if comp_name == "R1" and pin_name == "pin2":
                    pin2_net = net_root

        self.assertIsNotNone(pin1_net)
        self.assertIsNotNone(pin2_net)
        self.assertNotEqual(pin1_net, pin2_net)

    def test_wire_connects_two_components(self):
        # Battery+ at row5, R1 pin1 also at row5 -> should share a net
        battery = Battery("BAT1", ("main", 5, "a"), ("main", 15, "a"), voltage=5.0)
        r1 = Resistor("R1", ("main", 5, "b"), ("main", 10, "a"), resistance_ohms=220)

        self.netlist.add_component(battery)
        self.netlist.add_component(r1)

        result = self.netlist.build_netlist()

        # find the net containing BAT1's positive pin
        shared_net = None
        for net_root, pins in result.items():
            if ("BAT1", "positive") in pins:
                shared_net = net_root

        self.assertIsNotNone(shared_net)
        self.assertIn(("R1", "pin1"), result[shared_net])

    def test_invalid_hole_raises_error(self):
        bad_led = LED("LED1", ("main", 999, "z"), ("main", 5, "a"))
        with self.assertRaises(ValueError):
            self.netlist.add_component(bad_led)

    def test_full_circuit_three_separate_nets(self):
        battery = Battery("BAT1", ("main", 5, "a"), ("main", 15, "a"), voltage=5.0)
        r1 = Resistor("R1", ("main", 5, "b"), ("main", 10, "a"), resistance_ohms=220)
        led1 = LED("LED1", ("main", 10, "b"), ("main", 15, "b"))

        self.netlist.add_component(battery)
        self.netlist.add_component(r1)
        self.netlist.add_component(led1)

        result = self.netlist.build_netlist()

        # a correctly wired series circuit should produce exactly 3 distinct nets
        self.assertEqual(len(result), 3)


if __name__ == "__main__":
    unittest.main()