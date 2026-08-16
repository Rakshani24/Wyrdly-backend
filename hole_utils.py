def parse_hole_key(key):
    """
    Converts a frontend hole key string like 'main-5-a' or 'top-plus-3'
    back into the tuple format your Breadboard model expects,
    e.g. ("main", 5, "a") or ("top_rail", "+", 3).
    """
    parts = key.split("-")

    if parts[0] == "main":
        # main-5-a -> ("main", 5, "a")
        return ("main", int(parts[1]), parts[2])

    if parts[0] == "top":
        # top-plus-3 -> ("top_rail", "+", 3)
        sign = "+" if parts[1] == "plus" else "-"
        return ("top_rail", sign, int(parts[2]))

    if parts[0] == "bottom":
        sign = "+" if parts[1] == "plus" else "-"
        return ("bottom_rail", sign, int(parts[2]))

    raise ValueError(f"Unrecognized hole key format: {key}")
if __name__ == "__main__":
    print(parse_hole_key("main-5-a"))       # expect ("main", 5, "a")
    print(parse_hole_key("top-plus-3"))     # expect ("top_rail", "+", 3)
    print(parse_hole_key("bottom-minus-7")) # expect ("bottom_rail", "-", 7)
