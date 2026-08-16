class Breadboard:
    """
    Models a standard half-size breadboard's electrical topology.
    
    Layout:
    - Two power rails at top, two at bottom (each is one continuous net)
    - Main area: rows 1-30, each row split into two groups:
        columns a-e (left of center gap) and columns f-j (right of center gap)
      Each 5-hole group is one electrically connected net.
    """

    def __init__(self):
        # net_id -> set of holes belonging to that net
        self.nets = {}
        # hole -> net_id (for fast lookup)
        self.hole_to_net = {}
        self._build_topology()

    def _add_hole_to_net(self, hole, net_id):
        if net_id not in self.nets:
            self.nets[net_id] = set()
        self.nets[net_id].add(hole)
        self.hole_to_net[hole] = net_id

    def _build_topology(self):
        # --- Power rails ---
        # Top rails: two separate nets (+ and -), each spans all columns
        for col in range(1, 51):  # 50 holes along a typical rail
            self._add_hole_to_net(("top_rail", "+", col), "top_rail_+")
            self._add_hole_to_net(("top_rail", "-", col), "top_rail_-")
            self._add_hole_to_net(("bottom_rail", "+", col), "bottom_rail_+")
            self._add_hole_to_net(("bottom_rail", "-", col), "bottom_rail_-")

        # --- Main terminal strip ---
        # Rows 1-30, each row has two separate 5-hole groups: a-e and f-j
        left_cols = ["a", "b", "c", "d", "e"]
        right_cols = ["f", "g", "h", "i", "j"]

        for row in range(1, 31):
            left_net_id = f"row{row}_left"
            right_net_id = f"row{row}_right"

            for col in left_cols:
                self._add_hole_to_net(("main", row, col), left_net_id)

            for col in right_cols:
                self._add_hole_to_net(("main", row, col), right_net_id)

    def are_connected(self, hole_a, hole_b):
        """Returns True if two holes are electrically connected (same net)."""
        net_a = self.hole_to_net.get(hole_a)
        net_b = self.hole_to_net.get(hole_b)
        if net_a is None or net_b is None:
            raise ValueError(f"Unknown hole: {hole_a if net_a is None else hole_b}")
        return net_a == net_b

    def get_net(self, hole):
        """Returns the net_id a hole belongs to."""
        return self.hole_to_net.get(hole)


# --- Quick manual test when you run this file directly ---
if __name__ == "__main__":
    board = Breadboard()

    # Same row, same side -> should be connected
    h1 = ("main", 12, "a")
    h2 = ("main", 12, "c")
    print(f"{h1} and {h2} connected? {board.are_connected(h1, h2)}  (expect True)")

    # Same row, opposite sides of the center gap -> should NOT be connected
    h3 = ("main", 12, "a")
    h4 = ("main", 12, "f")
    print(f"{h3} and {h4} connected? {board.are_connected(h3, h4)}  (expect False)")

    # Different rows -> should NOT be connected
    h5 = ("main", 12, "c")
    h6 = ("main", 13, "c")
    print(f"{h5} and {h6} connected? {board.are_connected(h5, h6)}  (expect False)")

    # Power rail holes -> should be connected across the whole rail
    h7 = ("top_rail", "+", 1)
    h8 = ("top_rail", "+", 40)
    print(f"{h7} and {h8} connected? {board.are_connected(h7, h8)}  (expect True)")

    # Top + rail vs top - rail -> should NOT be connected
    h9 = ("top_rail", "+", 1)
    h10 = ("top_rail", "-", 1)
    print(f"{h9} and {h10} connected? {board.are_connected(h9, h10)}  (expect False)")