class Component:
    """
    Base class for anything with pins plugged into breadboard holes.
    Subclasses (Resistor, LED, etc.) just define their pin NAMES --
    the placement logic is shared.
    """

    def __init__(self, name, pin_holes):
        self.name = name
        self.pin_holes = pin_holes

    def pins(self):
        return list(self.pin_holes.items())


class Resistor(Component):
    def __init__(self, name, pin1_hole, pin2_hole, resistance_ohms):
        super().__init__(name, {"pin1": pin1_hole, "pin2": pin2_hole})
        self.resistance_ohms = resistance_ohms


class LED(Component):
    def __init__(self, name, anode_hole, cathode_hole):
        super().__init__(name, {"anode": anode_hole, "cathode": cathode_hole})


class Battery(Component):
    def __init__(self, name, positive_hole, negative_hole, voltage):
        super().__init__(name, {"positive": positive_hole, "negative": negative_hole})
        self.voltage = voltage


class Capacitor(Component):
    def __init__(self, name, pin1_hole, pin2_hole, capacitance_farads):
        super().__init__(name, {"pin1": pin1_hole, "pin2": pin2_hole})
        self.capacitance_farads = capacitance_farads


class Switch(Component):
    def __init__(self, name, pin1_hole, pin2_hole):
        super().__init__(name, {"pin1": pin1_hole, "pin2": pin2_hole})
        self.is_closed = True


class Diode(Component):
    """
    Like an LED electrically (current flows one way only, anode -> cathode)
    but without light output. Used in rectifiers, flyback protection, etc.
    """
    def __init__(self, name, anode_hole, cathode_hole):
        super().__init__(name, {"anode": anode_hole, "cathode": cathode_hole})


class Inductor(Component):
    def __init__(self, name, pin1_hole, pin2_hole, inductance_henries):
        super().__init__(name, {"pin1": pin1_hole, "pin2": pin2_hole})
        self.inductance_henries = inductance_henries


class Transistor(Component):
    """
    SIMPLIFIED 2-pin representation: models only the collector-emitter path
    (the "main" current path a transistor switches). The base pin (which
    controls whether that path conducts) is NOT modeled yet -- the current
    placement UI only supports 2-pin components. Treat this as a stand-in
    for "a controllable switch in the circuit," not a full 3-terminal model.
    """
    def __init__(self, name, collector_hole, emitter_hole):
        super().__init__(name, {"collector": collector_hole, "emitter": emitter_hole})