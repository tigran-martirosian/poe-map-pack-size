from pack_size import calc


def test_multiplier_from_percent():
    assert calc.multiplier_from_percent(78) == 1.78


def test_contribution_is_rounded_down():
    assert calc.contribution(5, 1.78) == 8    # 8.9
    assert calc.contribution(7, 1.78) == 12   # 12.46
    assert calc.contribution(4, 1) == 4


def test_calculate_totals_and_describes_each_modifier():
    total, details = calc.calculate([("Fecund", 5), ("Twinned", 7)], 1.78)
    assert total == 8 + 12
    assert details == ["Fecund: 5 x 1.78 = 8", "Twinned: 7 x 1.78 = 12"]


def test_calculate_with_no_matches():
    assert calc.calculate([], 1.78) == (0, [])


def test_roll_percent_inside_the_range():
    assert calc.roll_percent(56, 56, 86) == 0
    assert calc.roll_percent(71, 56, 86) == 50
    assert calc.roll_percent(86, 56, 86) == 100
    assert calc.roll_percent(60, 56, 86) == 13.33
