import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from fault_detector import detect_exact_reversal


class TestReversalDetection(unittest.TestCase):

    def test_reversed_led_detected(self):
        expected_nets = [
            frozenset({("BAT1", "positive"), ("R1", "pin1")}),
            frozenset({("R1", "pin2"), ("LED1", "anode")}),
            frozenset({("LED1", "cathode"), ("BAT1", "negative")})
        ]
        # user's circuit: LED anode/cathode swapped
        user_nets = [
            frozenset({("BAT1", "positive"), ("R1", "pin1")}),
            frozenset({("R1", "pin2"), ("LED1", "cathode")}),
            frozenset({("LED1", "anode"), ("BAT1", "negative")})
        ]

        result = detect_exact_reversal(user_nets, expected_nets)
        self.assertEqual(result, ["LED1"])

    def test_correct_circuit_no_reversal(self):
        expected_nets = [
            frozenset({("BAT1", "positive"), ("R1", "pin1")}),
            frozenset({("R1", "pin2"), ("LED1", "anode")}),
            frozenset({("LED1", "cathode"), ("BAT1", "negative")})
        ]
        result = detect_exact_reversal(expected_nets, expected_nets)
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()