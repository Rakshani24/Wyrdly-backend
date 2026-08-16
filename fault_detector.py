def classify_faults(missing_nets, extra_nets, user_nets=None, expected_nets=None):
    faults = []
    missing_list = list(missing_nets)
    extra_list = list(extra_nets)

    matched_missing = set()
    matched_extra = set()

    # NEW: check for precise reversals first, if we have the full net lists
    reversed_components = []
    if user_nets is not None and expected_nets is not None:
        reversed_components = detect_exact_reversal(user_nets, expected_nets)
        for comp_name in reversed_components:
            faults.append({
                "type": "component_reversed",
                "component": comp_name,
                "detail": f"{comp_name} appears to be wired backwards -- try flipping its orientation."
            })

    # existing pattern-matching loop, but SKIP components we already
    # confirmed as exact reversals (avoid double-reporting)
    for m_net in missing_list:
        m_components = {pin[0] for pin in m_net}
        for e_net in extra_list:
            e_components = {pin[0] for pin in e_net}
            shared = m_components & e_components
            for comp_name in shared:
                if comp_name in reversed_components:
                    continue  # already reported precisely above
                faults.append({
                    "type": "possible_reversed_or_miswired_component",
                    "component": comp_name,
                    "detail": f"{comp_name}'s connections don't match the expected circuit -- "
                              f"check if it's reversed or wired to the wrong holes."
                })
            if shared:
                matched_missing.add(m_net)
                matched_extra.add(e_net)

    for m_net in missing_list:
        if m_net not in matched_missing:
            comps = [f"{c}.{p}" for c, p in m_net]
            faults.append({
                "type": "missing_connection",
                "detail": f"Expected these to be connected but they aren't: {comps}"
            })

    for e_net in extra_list:
        if e_net not in matched_extra:
            comps = [f"{c}.{p}" for c, p in e_net]
            faults.append({
                "type": "unexpected_connection",
                "detail": f"These are connected but shouldn't be: {comps}"
            })

    return faults
    
def get_pin_fingerprints(nets):
    """
    nets: a list of sets/lists, where each set contains (component, pin) tuples
          that are all electrically connected together.

    Returns: dict mapping (component, pin) -> frozenset of OTHER pins sharing
    that net (excluding the pin itself). This is the pin's "fingerprint" --
    who it's actually connected to.
    """
    fingerprints = {}
    for net in nets:
        net_list = list(net)
        for pin in net_list:
            others = frozenset(p for p in net_list if p != pin)
            fingerprints[pin] = others
    return fingerprints

def detect_exact_reversal(user_nets, expected_nets):
    """
    user_nets, expected_nets: both in the "list of frozensets of pins" shape
    (same shape produced by netlist_to_comparable_form / reference_to_comparable_form).

    Returns a list of component names that are EXACTLY reversed: pin A's
    real connections match pin B's expected connections, and vice versa.
    """
    user_fp = get_pin_fingerprints(user_nets)
    expected_fp = get_pin_fingerprints(expected_nets)

    # group pins by component, since we need to compare A vs B per-component
    components = {}
    for (comp, pin) in expected_fp:
        components.setdefault(comp, []).append(pin)

    reversed_components = []

    for comp, pins in components.items():
        if len(pins) != 2:
            continue  # only handles 2-pin components (LED, resistor) for now

        pin_a, pin_b = pins
        key_a = (comp, pin_a)
        key_b = (comp, pin_b)

        # need all four fingerprints to exist to compare
        if key_a not in user_fp or key_b not in user_fp:
            continue

        user_a = user_fp[key_a]
        user_b = user_fp[key_b]
        expected_a = expected_fp[key_a]
        expected_b = expected_fp[key_b]

        # the swap condition: A's real fingerprint == B's expected fingerprint,
        # AND B's real fingerprint == A's expected fingerprint
        is_swapped = (user_a == expected_b) and (user_b == expected_a)

        # sanity check: make sure it's ACTUALLY different from correct
        # (otherwise a correctly-wired component would trivially "match itself")
        is_actually_wrong = (user_a != expected_a) or (user_b != expected_b)

        if is_swapped and is_actually_wrong:
            reversed_components.append(comp)

    return reversed_components
