import math


def multiplier_from_percent(percent):
    return percent / 100 + 1


def contribution(pack_size, multiplier):
    return math.floor(pack_size * multiplier)


def calculate(matches, multiplier):
    """matches is a list of (name, pack size); returns the total and one text line per modifier."""
    total = 0
    details = []
    for name, pack_size in matches:
        part = contribution(pack_size, multiplier)
        total += part
        details.append(f"{name}: {pack_size} x {multiplier:g} = {part}")
    return total, details


def roll_percent(total, low, high):
    return max(0, round((total - low) / (high - low) * 100, 2))
