import json
from fault_detector import classify_faults
def netlist_to_comparable_form(netlist_result):
    """
    Converts your build_netlist() output (net_root -> list of pins)
    into a list of frozensets of pins, ignoring the actual net_root
    labels (since those are arbitrary/positional and shouldn't matter).
    """
    return [frozenset(pins) for pins in netlist_result.values()]


def reference_to_comparable_form(expected_nets):
    """
    Converts the reference JSON's expected_nets into the same shape:
    a list of frozensets of (component_name, pin_name) tuples.
    """
    result = []
    for net in expected_nets:
        pins = frozenset(tuple(pin) for pin in net["pins"])
        result.append(pins)
    return result


def compare_netlists(user_netlist_result, expected_nets):
    """
    Returns a simple report: which expected nets are missing from the
    user's circuit, and which extra/unexpected nets the user has.
    This is the crudest possible version of Module 5 -- exact set
    matching. Real fault localization comes later.
    """
    user_nets = set(netlist_to_comparable_form(user_netlist_result))
    expected = set(reference_to_comparable_form(expected_nets))

    missing = expected - user_nets   # nets the reference expects but user doesn't have
    extra = user_nets - expected 
    faults = classify_faults(missing, extra, user_nets=list(user_nets), expected_nets=list(expected))

    return {
        "correct": len(missing) == 0 and len(extra) == 0,
        "missing_nets": missing,
        "extra_nets": extra,
        "faults": faults
    }
if __name__ == "__main__":
    import json
    from model import Breadboard
    from wiring import NetlistBuilder
    from components import Resistor, LED, Battery

    # build the CORRECT circuit
    board = Breadboard()
    netlist = NetlistBuilder(board)
    battery = Battery("BAT1", ("main", 5, "a"), ("main", 15, "a"), voltage=5.0)
    r1 = Resistor("R1", ("main", 5, "b"), ("main", 10, "a"), resistance_ohms=220)
    led1 = LED("LED1", ("main", 10, "b"), ("main", 15, "b"))
    netlist.add_component(battery)
    netlist.add_component(r1)
    netlist.add_component(led1)
    user_result = netlist.build_netlist()

    # load the reference
    with open("reference_circuits/led_resistor.json") as f:
        reference = json.load(f)

    report = compare_netlists(user_result, reference["expected_nets"])
    print("Correct:", report["correct"])
    print("Missing nets:", report["missing_nets"])
    print("Extra nets:", report["extra_nets"])
    print("\nFaults detected:")
    for f in report["faults"]:
        print(f" - [{f['type']}] {f['detail']}")
