#!/usr/bin/env python3
"""Official IELTS Score Calculator and Rounding Algorithm.

IELTS Writing Overall Band Rounding Rules:
- The 4 criteria (Task Achievement/Response, Coherence & Cohesion, Lexical Resource,
  Grammatical Range & Accuracy) are equally weighted (25% each).
- The arithmetic mean = (C1 + C2 + C3 + C4) / 4.
- If the mean ends in:
    .00 -> rounds to .0
    .125 -> rounds to .0
    .25 -> rounds UP to .5
    .375 -> rounds UP to .5
    .50 -> stays at .5
    .625 -> rounds UP to .5 (if < .75) or down?
    Let's verify the official IELTS rule:
    Official British Council / IDP rule:
    - If average ends in .25, it rounds UP to the next half band (.5).
    - If average ends in .75, it rounds UP to the next whole band (e.g. 6.75 -> 7.0).
    - If average ends in .125 -> .0 (e.g. 6.125 -> 6.0)
    - If average ends in .375 -> .5 (e.g. 6.375 -> 6.5)
    - If average ends in .625 -> .5 (e.g. 6.625 -> 6.5)
    - If average ends in .875 -> next whole band (e.g. 6.875 -> 7.0)
"""

from __future__ import annotations
import sys

def calculate_ielts_band(c1: float, c2: float, c3: float, c4: float) -> tuple[float, float]:
    """Calculate exact mean and rounded IELTS band from 4 criteria scores.
    
    Returns:
        (exact_mean, rounded_band)
    """
    raw_mean = (c1 + c2 + c3 + c4) / 4.0
    exact_mean = round(raw_mean, 2)
    
    whole = int(raw_mean)
    fraction = raw_mean - whole
    
    # Official IELTS rounding thresholds:
    if fraction < 0.25:
        # e.g., 0.125 -> rounds down to whole band
        rounded = float(whole)
    elif fraction < 0.75:
        # e.g., 0.25, 0.375, 0.5, 0.625 -> rounds to .5
        rounded = float(whole) + 0.5
    else:
        # e.g., 0.75, 0.875 -> rounds UP to next whole band
        rounded = float(whole + 1)
        
    return exact_mean, rounded

def run_tests():
    test_cases = [
        # (c1, c2, c3, c4, expected_mean, expected_band)
        (7.0, 6.5, 6.5, 6.5, 6.63, 6.5),  # Hoang Minh (Task 1 & Task 2)
        (6.0, 6.0, 6.0, 5.5, 5.88, 6.0),  # Thuy Vy (Task 1)
        (5.5, 6.0, 5.5, 5.0, 5.50, 5.5),  # Thuy Vy (Task 2)
        (5.5, 6.0, 5.5, 5.5, 5.63, 5.5),  # Thomas (Task 1)
        (5.0, 5.5, 5.5, 5.0, 5.25, 5.5),  # Thomas (Task 2)
        (6.5, 6.5, 6.5, 7.5, 6.75, 7.0),  # .75 rounds up to next whole
        (6.0, 6.0, 6.0, 7.0, 6.25, 6.5),  # .25 rounds up to half band
        (6.0, 6.0, 6.0, 6.5, 6.12, 6.0),  # .125 rounds down to 6.0
        (6.0, 6.5, 6.5, 6.5, 6.38, 6.5),  # .375 rounds to 6.5
        (6.5, 7.0, 7.0, 7.0, 6.88, 7.0),  # .875 rounds to 7.0
    ]
    all_ok = True
    for c1, c2, c3, c4, exp_m, exp_b in test_cases:
        m, b = calculate_ielts_band(c1, c2, c3, c4)
        ok = (abs(m - exp_m) <= 0.01 and b == exp_b)
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] Scores ({c1}, {c2}, {c3}, {c4}) -> Mean: {m} (expected {exp_m}), Band: {b} (expected {exp_b})")
        if not ok:
            all_ok = False
    if all_ok:
        print("\nAll 10 test cases PASSED successfully!")
    else:
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
    elif len(sys.argv) == 5:
        c1, c2, c3, c4 = map(float, sys.argv[1:5])
        mean, band = calculate_ielts_band(c1, c2, c3, c4)
        print(f"Mean: {mean:.2f}, Band: {band:.1f}")
    else:
        print("Usage: score_calculator.py <c1> <c2> <c3> <c4> | score_calculator.py --test")
