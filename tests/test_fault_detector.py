import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from fault_detector import classify_faults


class TestFaultDetector(unittest.TestCase):

    def test_reversed_component_produces_single_fault(self):
        # Simulate: LED's anode/cathode nets are swapped vs expected.
        # missing_nets: what SHOULD exist but doesn't
        # extra_nets: what DOES exist but shouldn't
        missing = {
            frozenset({("R1", "pin2"), ("LED1", "anode")}),
            frozenset({("LED1", "cathode"), ("BAT1", "negative")})
        }
        extra = {
            frozenset({("R1", "pin2"), ("LED1", "cathode")}),
            frozenset({("LED1", "anode"), ("BAT1", "negative")})
        }

        faults = classify_faults(missing, extra)

        reversed_faults = [f for f in faults if f["type"] == "possible_reversed_or_miswired_component"]
        generic_faults = [f for f in faults if f["type"] in ("missing_connection", "unexpected_connection")]

        # Should recognize this as a component-level issue, not raw leftovers
        self.assertTrue(len(reversed_faults) > 0)
        self.assertEqual(len(generic_faults), 0)

    def test_plain_missing_wire_produces_generic_fault(self):
        # A net that's expected but totally missing, no matching extra net
        # involving the same component -- e.g. user just forgot a wire.
        missing = {
            frozenset({("R1", "pin2"), ("LED1", "anode")})
        }
        extra = set()  # nothing unexpected, just an incomplete circuit

        faults = classify_faults(missing, extra)

        self.assertEqual(len(faults), 1)
        self.assertEqual(faults[0]["type"], "missing_connection")

    def test_no_faults_when_nothing_wrong(self):
        faults = classify_faults(set(), set())
        self.assertEqual(len(faults), 0)


if __name__ == "__main__":
    unittest.main()