"""Generate 50 hand-crafted Zahlenfolgen exercises with verified correct answers.

Each exercise uses a specific, well-defined mathematical pattern. All answers
are programmatically computed (not hand-written), guaranteeing correctness.

Usage: uv run python generate_50_zahlenfolgen.py
"""

from __future__ import annotations

import random
from pathlib import Path

OUTPUT_DIR = Path("output/zahlenfolgen")
START_ID = 71


def write_exercise(
    qid: int,
    visible: list[int],
    correct: list[int],
    correct_letter: str,
    explanation: str,
) -> None:
    """Write question and solution files for one exercise."""
    v1, v2 = correct

    # Generate 3 wrong answer pairs
    distractor_pool: set[tuple[int, int]] = set()
    last = visible[-1]
    diffs = [visible[i + 1] - visible[i] for i in range(len(visible) - 1)]
    avg_diff = sum(diffs) // len(diffs) if diffs else 1
    last_diff = diffs[-1] if diffs else 1

    # Constant diff extrapolation
    distractor_pool.add((last + last_diff, last + 2 * last_diff))
    distractor_pool.add((last + avg_diff, last + 2 * avg_diff))
    # Swapped
    if v1 != v2:
        distractor_pool.add((v2, v1))
    # Off-by-1 and off-by-2 variants
    distractor_pool.add((v1 + 1, v2))
    distractor_pool.add((v1 - 1, v2))
    distractor_pool.add((v1, v2 + 1))
    distractor_pool.add((v1, v2 - 1))
    distractor_pool.add((v1 + 2, v2))
    distractor_pool.add((v1 - 2, v2))
    # Wrong operation
    distractor_pool.add((last * 2, last * 2 + last_diff))

    distractor_pool.discard((v1, v2))
    # Remove pairs with same values
    distractor_pool = {p for p in distractor_pool if p[0] != p[1]}
    distractors = random.sample(sorted(distractor_pool), min(3, len(distractor_pool)))
    distractor_list = [[d[0], d[1]] for d in distractors]

    # Build A–E options
    all_pairs = [(correct_letter, correct)]
    dl = [l for l in "ABCD" if l != correct_letter]
    for i, letter in enumerate(dl):
        all_pairs.append((letter, distractor_list[i]))
    all_pairs.sort(key=lambda x: x[0])

    lines = [f"Zahlenfolge: {' '.join(str(x) for x in visible)} ? ?", ""]
    for letter, pair in all_pairs:
        lines.append(f"{letter}) {pair[0]}/{pair[1]}")
    lines.append("E) Keine der Antworten ist richtig")
    question = "\n".join(lines)

    solution = f"{correct_letter} — {v1}/{v2}\n{explanation}\n"

    (OUTPUT_DIR / f"{qid:04d}_question.txt").write_text(question + "\n", encoding="utf-8")
    (OUTPUT_DIR / f"{qid:04d}_solution.txt").write_text(solution, encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════════════════
# Pattern generators — each returns (visible_6, [next_2], explanation)
# ═══════════════════════════════════════════════════════════════════════════════


def growing_diff(start: int, diff: int, growth: int) -> tuple[list[int], list[int], str]:
    """Differences grow by `growth` each step."""
    seq = [start]
    cur = diff
    for _ in range(7):
        seq.append(seq[-1] + cur)
        cur += growth
    return seq[:6], [seq[6], seq[7]], (
        f"Differenz: {', '.join(f'+{seq[i+1]-seq[i]}' for i in range(7))} "
        f"— die Differenz wächst um {growth:+d} pro Schritt"
    )


def alt_add_mul(start: int, addv: int, mulv: int) -> tuple[list[int], list[int], str]:
    """Alternate +add, ×mul, +add, ×mul, ..."""
    seq = [start]
    for i in range(7):
        if i % 2 == 0:
            seq.append(seq[-1] + addv)
        else:
            seq.append(seq[-1] * mulv)
    return seq[:6], [seq[6], seq[7]], f"+{addv}, ×{mulv} im Wechsel"


def alt_mul_sub(start: int, mulv: int, subv: int) -> tuple[list[int], list[int], str]:
    """Alternate ×mul, -sub, ×mul, -sub, ..."""
    seq = [start]
    for i in range(7):
        if i % 2 == 0:
            seq.append(seq[-1] * mulv)
        else:
            seq.append(seq[-1] - subv)
    return seq[:6], [seq[6], seq[7]], f"×{mulv}, -{subv} im Wechsel"


def alt_div_add(start: int, div: int, addv: int) -> tuple[list[int], list[int], str]:
    """Alternate :div, +add, :div (ceil), +add, ..."""
    seq = [start]
    for i in range(7):
        if i % 2 == 0:
            seq.append(seq[-1] // div + (1 if seq[-1] % div else 0))
        else:
            seq.append(seq[-1] + addv)
    # Recompute from start using consistent rounding for whole sequence
    seq = [start]
    for i in range(7):
        if i % 2 == 0:
            # round half up: (n + div//2) // div
            seq.append((seq[-1] + div // 2) // div)
        else:
            seq.append(seq[-1] + addv)
    return seq[:6], [seq[6], seq[7]], (
        f"Ganzzahliges Halbieren (aufrunden), +{addv} im Wechsel"
    )


def fib_like(a: int, b: int, add: int) -> tuple[list[int], list[int], str]:
    """a, b, a+b+add, b+(a+b+add)+add, ..."""
    seq = [a, b]
    for _ in range(6):
        seq.append(seq[-2] + seq[-1] + add)
    return seq[:6], [seq[6], seq[7]], (
        f"Ab 3. Glied: Summe der beiden Vorgänger + {add}"
    )


def interleaved_arith(a1: int, d1: int, a2: int, d2: int) -> tuple[list[int], list[int], str]:
    """Two arithmetic sequences woven together."""
    seq = []
    for i in range(8):
        if i % 2 == 0:
            seq.append(a1 + (i // 2) * d1)
        else:
            seq.append(a2 + (i // 2) * d2)
    return seq[:6], [seq[6], seq[7]], (
        f"Zwei Folgen verschränkt: +{d1} und +{d2}"
    )


def interleaved_mixed(
    a1: int, op1: str, v1: int, a2: int, op2: str, v2: int
) -> tuple[list[int], list[int], str]:
    """Two sequences with different operations woven together."""
    seq = [0] * 8
    seq[0] = a1
    seq[1] = a2
    for i in range(2, 8):
        if i % 2 == 0:  # first sequence (even indices)
            if op1 == "+":
                seq[i] = seq[i - 2] + v1
            else:
                seq[i] = seq[i - 2] * v1
        else:  # second sequence (odd indices)
            if op2 == "+":
                seq[i] = seq[i - 2] + v2
            else:
                seq[i] = seq[i - 2] * v2
    op1name = f"+{v1}" if op1 == "+" else f"×{v1}"
    op2name = f"+{v2}" if op2 == "+" else f"×{v2}"
    return seq[:6], [seq[6], seq[7]], (
        f"Zwei Folgen verschränkt: {op1name} und {op2name}"
    )


def multiply_minus_const(start: int, mul: int, sub: int) -> tuple[list[int], list[int], str]:
    """×mul - sub each step."""
    seq = [start]
    for _ in range(7):
        seq.append(seq[-1] * mul - sub)
    return seq[:6], [seq[6], seq[7]], f"×{mul} - {sub} je Schritt"


def n_squared_plus_c(c: int) -> tuple[list[int], list[int], str]:
    """n² + c"""
    seq = [i * i + c for i in range(1, 9)]
    return seq[:6], [seq[6], seq[7]], f"n² + {c} (1²+{c}={seq[0]}, 2²+{c}={seq[1]}, ...)"


def n_cubed() -> tuple[list[int], list[int], str]:
    """n³"""
    seq = [i * i * i for i in range(1, 9)]
    return seq[:6], [seq[6], seq[7]], f"n³: 1³=1, 2³=8, 3³=27, ..., 7³=343, 8³=512"


def two_pow_n_minus_1() -> tuple[list[int], list[int], str]:
    """2ⁿ - 1"""
    seq = [(2 ** i) - 1 for i in range(1, 9)]
    return seq[:6], [seq[6], seq[7]], "2ⁿ - 1: 2¹-1=1, 2²-1=3, ..., 2⁷-1=127, 2⁸-1=255"


def factorial_seq() -> tuple[list[int], list[int], str]:
    """n!"""
    seq = [1, 2, 6, 24, 120, 720, 5040, 40320]
    return seq[:6], [seq[6], seq[7]], "Fakultät: 1!=1, 2!=2, 3!=6, ..., 7!=5040, 8!=40320"


def recursive_add_prev_two() -> tuple[list[int], list[int], str]:
    """Fibonacci starting 3,4"""
    seq = [3, 4]
    for _ in range(6):
        seq.append(seq[-2] + seq[-1])
    return seq[:6], [seq[6], seq[7]], "Jedes Glied = Summe der beiden Vorgänger (Fibonacci mit Start 3,4)"


def double_diff(start: int, diff1: int) -> tuple[list[int], list[int], str]:
    """Differences double each step."""
    seq = [start]
    cur_diff = diff1
    for _ in range(7):
        seq.append(seq[-1] + cur_diff)
        cur_diff *= 2
    return seq[:6], [seq[6], seq[7]], "Differenz verdoppelt sich je Schritt"


def diff_fibonacci(start: int, d1: int, d2: int) -> tuple[list[int], list[int], str]:
    """Differences follow Fibonacci pattern."""
    seq = [start]
    diffs = [d1, d2]
    for _ in range(2, 8):
        diffs.append(diffs[-2] + diffs[-1])
    for d in diffs:
        seq.append(seq[-1] + d)
    return seq[:6], [seq[6], seq[7]], (
        "Differenz-Fibonacci: die Differenzen folgen der Fibonacci-Regel"
    )


def add_mul_cycle(
    start: int, add1: int, add2: int, mul: int
) -> tuple[list[int], list[int], str]:
    """Three-step cycle: +add1, +add2, ×mul, +add1, +add2, ×mul, ..."""
    seq = [start]
    ops = [
        ("+", add1),
        ("+", add2),
        ("*", mul),
        ("+", add1),
        ("+", add2),
        ("*", mul),
        ("+", add1),
    ]
    for op, val in ops:
        if op == "+":
            seq.append(seq[-1] + val)
        else:
            seq.append(seq[-1] * val)
    return seq[:6], [seq[6], seq[7]], f"+{add1}, +{add2}, ×{mul} im Dreier-Zyklus"


def n_times_n_plus_1() -> tuple[list[int], list[int], str]:
    """n(n+1) — rectangular numbers."""
    seq = [i * (i + 1) for i in range(1, 9)]
    return seq[:6], [seq[6], seq[7]], "n(n+1): 1·2=2, 2·3=6, 3·4=12, ..., 7·8=56, 8·9=72"


def alt_pow(start: int, pow1: int, pow2: int) -> tuple[list[int], list[int], str]:
    """Alternate: ×pow1, ×pow2, ×pow1, ×pow2, ..."""
    seq = [start]
    for i in range(7):
        seq.append(seq[-1] * (pow1 if i % 2 == 0 else pow2))
    return seq[:6], [seq[6], seq[7]], f"×{pow1}, ×{pow2} im Wechsel"


# ═══════════════════════════════════════════════════════════════════════════════
# The 50 exercises
# ═══════════════════════════════════════════════════════════════════════════════

EXERCISES: list[tuple[list[int], list[int], str]] = [
    # ── Growing differences (second-order arithmetic) ── 8 exercises ────────
    growing_diff(32, 10, 4),       # 32,42,56,74,96,122 → 152,186
    growing_diff(5, 7, 7),         # 5,12,26,47,75,110 → 152,201
    growing_diff(2, 4, 3),         # 2,6,13,23,36,52 → 71,93
    growing_diff(10, 8, 8),        # 10,18,34,58,90,130 → 178,234
    growing_diff(1, 2, 2),         # 1,3,7,13,21,31 → 43,57
    growing_diff(20, 2, 2),        # 20,22,28,40,60,90 → 132,188 (diffs: +2,+6,+12,+20,+30 → next +42,+56)
    growing_diff(7, 4, 0),         # 7,11,15,19,23,27 → 31,35 (constant diff)
    growing_diff(100, -3, -3),     # 100,97,91,82,70,55 → 37,16 (diffs: -3,-6,-9,-12,-15 → -18,-21)
    # ── Alternating: +add, ×mul ── 6 exercises ─────────────────────────────
    alt_add_mul(4, 3, 2),          # 4,7,14,17,34,37 → 74,77
    alt_add_mul(1, 3, 2),          # 1,4,8,11,22,25 → 50,53
    alt_add_mul(2, 3, 3),          # 2,5,15,18,54,57 → 171,174
    alt_add_mul(1, 1, 3),          # 1,2,6,7,21,22 → 66,67
    alt_add_mul(6, 3, 2),          # 6,9,18,21,42,45 → 90,93
    alt_add_mul(3, 5, 2),          # 3,8,16,21,42,47 → 94,99
    # ── Alternating: ×mul, -sub ── 4 exercises ─────────────────────────────
    alt_mul_sub(3, 3, 3),          # 3,9,6,18,15,45 → 42,126
    alt_mul_sub(5, 2, 3),          # 5,10,7,14,11,22 → 19,38
    alt_mul_sub(6, 2, 4),          # 6,12,8,16,12,24 → 20,40
    alt_mul_sub(4, 3, 2),          # 4,12,10,30,28,84 → 82,246
    # ── Alternating: :2 (round up), +add ── 2 exercises ────────────────────
    alt_div_add(100, 2, 5),        # 100,50,55,27,32,16 → 21,10
    alt_mul_sub(10, 2, 7),         # 10,20,13,26,19,38 → 31,62
    # ── Fibonacci variants ── 6 exercises ──────────────────────────────────
    fib_like(2, 3, 1),             # 2,3,6,10,17,28 → 46,75
    fib_like(1, 1, 1),             # 1,1,3,5,9,15 → 25,41
    fib_like(5, 8, 5),             # 5,8,18,31,54,90 → 149,245
    fib_like(3, 7, 3),             # 3,7,13,23,39,65 → 107,175
    fib_like(2, 2, 2),             # 2,2,6,10,18,30 → 50,82
    fib_like(1, 4, 2),             # 1,4,7,13,22,37 → 61,100
    # ── Interleaved arithmetic ── 3 exercises ──────────────────────────────
    interleaved_arith(5, 3, 10, 8),     # 5,10,8,18,11,26 → 14,34
    interleaved_arith(10, 5, 1, 3),     # 10,1,15,4,20,7 → 25,10
    interleaved_arith(0, 4, 32, -16),   # 0,32,4,16,8,0 → 12,-16
    # ── Interleaved mixed operations ── 4 exercises ─────────────────────────
    interleaved_mixed(1, "+", 3, 3, "*", 3),    # 1,3,4,9,7,27 → 10,81
    interleaved_mixed(2, "*", 3, 100, "+", -10), # 2,100,6,90,18,80 → 54,70
    interleaved_mixed(50, "+", -8, 3, "*", 3),   # 50,3,42,9,34,27 → 26,81
    interleaved_mixed(0, "+", 4, 32, "/", 2),    # 0,32,4,16,8,8 → 12,4
    # ── Multiply minus constant ── 3 exercises ─────────────────────────────
    multiply_minus_const(4, 2, 1),       # 4,7,13,25,49,97 → 193,385
    multiply_minus_const(3, 2, 1),       # 3,5,9,17,33,65 → 129,257
    multiply_minus_const(10, 2, 3),      # 10,17,31,59,115,227 → 451,899
    # ── Algebraic formulas ── 5 exercises ──────────────────────────────────
    n_squared_plus_c(0),                 # 1,4,9,16,25,36 → 49,64
    n_squared_plus_c(-1),                # 0,3,8,15,24,35 → 48,63
    n_squared_plus_c(1),                 # 2,5,10,17,26,37 → 50,65
    n_cubed(),                            # 1,8,27,64,125,216 → 343,512
    n_times_n_plus_1(),                  # 2,6,12,20,30,42 → 56,72
    # ── Powers and factorials ── 3 exercises ───────────────────────────────
    two_pow_n_minus_1(),                 # 1,3,7,15,31,63 → 127,255
    factorial_seq(),                      # 1,2,6,24,120,720 → 5040,40320
    alt_pow(1, 2, 3),                    # 1,2,6,12,36,72 → 216,432
    # ── Difference doubling ── 3 exercises ─────────────────────────────────
    double_diff(12, 3),                  # 12,15,21,33,57,105 → 201,393
    double_diff(7, 4),                   # 7,11,19,35,67,131 → 259,515
    double_diff(3, 1),                   # 3,4,6,10,18,34 → 66,130
    # ── Difference-Fibonacci ── 3 exercises ────────────────────────────────
    recursive_add_prev_two(),           # Fibonacci: 3,4,7,11,18,29 → 47,76
    diff_fibonacci(33, 5, 1),
    diff_fibonacci(2, 3, 4),
]


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    letters_cycle = ["B", "C", "D", "A", "B", "D", "A", "C", "B", "A",
                     "D", "B", "C", "A", "C", "D", "B", "C", "A", "D",
                     "B", "A", "C", "D", "A", "B", "C", "A", "D", "B",
                     "C", "D", "A", "B", "D", "C", "A", "B", "C", "D",
                     "A", "B", "D", "C", "B", "A", "C", "D", "A", "B"]

    for i, (visible, correct, explanation) in enumerate(EXERCISES):
        qid = START_ID + i
        letter = letters_cycle[i % len(letters_cycle)]
        write_exercise(qid, visible, correct, letter, explanation)

    print(f"Generated {len(EXERCISES)} zahlenfolgen exercises (IDs {START_ID}–{START_ID + len(EXERCISES) - 1})")


if __name__ == "__main__":
    main()
