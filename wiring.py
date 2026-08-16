from components import Resistor, LED, Battery
class NetlistBuilder:
    """
    Takes a Breadboard's base topology and merges nets together as wires
    are added. This is a Union-Find (Disjoint Set Union) structure.

    Why Union-Find: placing a wire between hole A and hole B means
    "the net A belongs to and the net B belongs to are now the SAME net."
    Union-Find is the standard, efficient algorithm for exactly this kind
    of "merge these groups together" problem.
    """

    def __init__(self, breadboard):
        self.board = breadboard
        # parent[net_id] = net_id it points to; a net is its own "root"
        # if parent[net_id] == net_id
        self.parent = {net_id: net_id for net_id in breadboard.nets}
        self.wires = []
        self.components = {}  # keep a log of placed wires for later (undo, display, etc)

    def _find_root(self, net_id):
        """
        Follows parent pointers until it finds the ultimate root net.
        'Path compression': while we're at it, point every node directly
        at the root, so future lookups are instant. This is the classic
        Union-Find optimization — without it, long chains of merges get slow.
        """
        if self.parent[net_id] != net_id:
            self.parent[net_id] = self._find_root(self.parent[net_id])
        return self.parent[net_id]

    def add_wire(self, hole_a, hole_b):
        """Places a wire between two holes, merging their nets."""
        net_a = self.board.get_net(hole_a)
        net_b = self.board.get_net(hole_b)

        if net_a is None or net_b is None:
            raise ValueError("One of the wire's endpoints is not a valid hole")

        root_a = self._find_root(net_a)
        root_b = self._find_root(net_b)

        if root_a != root_b:
            # merge: point one root at the other
            self.parent[root_b] = root_a

        self.wires.append((hole_a, hole_b))

    def are_connected(self, hole_a, hole_b):
        """
        Now checks connectivity INCLUDING wires — this supersedes the
        Breadboard's own are_connected, which only knows about the
        physical board, not user-placed wires.
        """
        net_a = self.board.get_net(hole_a)
        net_b = self.board.get_net(hole_b)
        if net_a is None or net_b is None:
            raise ValueError("Unknown hole")
        return self._find_root(net_a) == self._find_root(net_b)

    def get_all_nets(self):
        """
        Groups all holes into their FINAL merged nets (after wires).
        Returns a dict: root_net_id -> set of holes.
        This is essentially your first version of a 'netlist' —
        exactly what Module 3 needs to produce.
        """
        groups = {}
        for net_id, holes in self.board.nets.items():
            root = self._find_root(net_id)
            groups.setdefault(root, set()).update(holes)
        return groups
    def add_component(self, component):
        """
        Placing a component is electrically just like placing a wire
        between each pair of its pins... except we DON'T want to merge
        a resistor's two pins into the same net (a resistor separates
        two different nets, it doesn't join them like a wire does).
        
        Instead, we just record which net each pin lands in.
        """
        
        
        pin_nets = {}
        for pin_name, hole in component.pins():
            net_id = self.board.get_net(hole)
            if net_id is None:
                raise ValueError(f"{component.name} pin '{pin_name}' is in an unknown hole: {hole}")
            root = self._find_root(net_id)
            pin_nets[pin_name] = root
        
        self.components[component.name] = {
            "component": component,
            "pin_nets": pin_nets
        }
    def build_netlist(self):
        netlist = {}
        for comp_name, data in self.components.items():
            for pin_name, net_root in data["pin_nets"].items():
                netlist.setdefault(net_root, []).append((comp_name, pin_name))
        return netlist    

if __name__ == "__main__":
    from model import Breadboard

    board = Breadboard()
    netlist = NetlistBuilder(board)

    battery = Battery("BAT1", ("main", 5, "a"), ("main", 15, "a"), voltage=5.0)
    r1 = Resistor("R1", ("main", 5, "b"), ("main", 10, "a"), resistance_ohms=220)
    led1 = LED("LED1", ("main", 10, "b"), ("main", 15, "b"))

    netlist.add_component(battery)
    netlist.add_component(r1)
    netlist.add_component(led1)

    result = netlist.build_netlist()
    for net_root, pins in result.items():
        print(f"{net_root}: {pins}")