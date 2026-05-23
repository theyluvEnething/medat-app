"""Generate synthetic Zahlenfolgen exercises.

Produces flat NN_question.txt + NN_solution.txt files that merge seamlessly
with parsed PDF output. IDs continue from the highest existing ID.

Patterns covered: arithmetic, geometric, alternating, quadratic, Fibonacci,
interleaved, prime-based, digit manipulation, cumulative, and more.

Output format matches the real MedAT: two question marks (next two terms),
answer as "X/Y", five multiple-choice options with E always "none correct".
"""

from __future__ import annotations

import math
import random
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════
# Pattern generators
# ═══════════════════════════════════════════════════════════════════════════

def _fmt(n: int) -> str:
    return str(n)


def arithmetic(start: int, diff: int, length: int = 8) -> tuple[list[int], list[int]]:
    """a, a+d, a+2d, ..."""
    seq = [start + i * diff for i in range(length)]
    return seq, [seq[6], seq[7]]


def geometric(start: int, ratio: int, length: int = 8) -> tuple[list[int], list[int]]:
    """a, a*r, a*r², ..."""
    seq = [start * (ratio ** i) for i in range(length)]
    return seq, [seq[6], seq[7]]


def alternating(
    start: int, add_val: int, mul_val: int, length: int = 8
) -> tuple[list[int], list[int]]:
    """+add, ×mul, +add, ×mul, ..."""
    seq = [start]
    for i in range(length - 1):
        if i % 2 == 0:
            seq.append(seq[-1] + add_val)
        else:
            seq.append(seq[-1] * mul_val)
    return seq, [seq[6], seq[7]]


def quadratic(start: int, length: int = 8) -> tuple[list[int], list[int]]:
    """Sequence of n² + start, differences grow by 2 each step."""
    seq = [start + i * i for i in range(length)]
    return seq, [seq[6], seq[7]]


def fibonacci_like(a: int, b: int, length: int = 8) -> tuple[list[int], list[int]]:
    """a, b, a+b, b+(a+b), ..."""
    seq = [a, b]
    for _ in range(length - 2):
        seq.append(seq[-2] + seq[-1])
    return seq, [seq[6], seq[7]]


def interleaved(
    a1: int, d1: int, a2: int, d2: int, length: int = 8
) -> tuple[list[int], list[int]]:
    """Two arithmetic sequences woven together: a1, a2, a1+d1, a2+d2, ..."""
    seq = []
    for i in range(length):
        if i % 2 == 0:
            seq.append(a1 + (i // 2) * d1)
        else:
            seq.append(a2 + (i // 2) * d2)
    return seq, [seq[6], seq[7]]


def difference_growth(
    start: int, diff: int, growth: int, length: int = 8
) -> tuple[list[int], list[int]]:
    """Second-order: differences grow by `growth` each step."""
    seq = [start]
    cur_diff = diff
    for _ in range(length - 1):
        seq.append(seq[-1] + cur_diff)
        cur_diff += growth
    return seq, [seq[6], seq[7]]


def prime_sequence(skip: int, length: int = 8) -> tuple[list[int], list[int]]:
    """Consecutive primes starting from the skip-th prime."""
    primes = _first_n_primes(skip + length + 2)
    seq = primes[skip : skip + length]
    return seq, [seq[6], seq[7]]


def _first_n_primes(n: int) -> list[int]:
    """Sieve for the first n primes."""
    if n < 1:
        return []
    limit = max(50, n * (int(math.log(n)) + 3))
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    primes: list[int] = []
    for p in range(2, limit + 1):
        if sieve[p]:
            primes.append(p)
            if len(primes) == n:
                return primes
            for m in range(p * p, limit + 1, p):
                sieve[m] = False
    return primes


def multiplicative_alternating(
    start: int, mul1: int, mul2: int, length: int = 8
) -> tuple[list[int], list[int]]:
    """×mul1, ×mul2, ×mul1, ×mul2, ..."""
    seq = [start]
    for i in range(length - 1):
        mul = mul1 if i % 2 == 0 else mul2
        seq.append(seq[-1] * mul)
    return seq, [seq[6], seq[7]]


def digit_reverse(start: int, add: int, length: int = 8) -> tuple[list[int], list[int]]:
    """Reverse digits, then add constant, reverse, add, ..."""
    seq = [start]
    for i in range(length - 1):
        if i % 2 == 0:
            seq.append(int(str(seq[-1])[::-1]))
        else:
            seq.append(seq[-1] + add)
    return seq, [seq[6], seq[7]]


def cubic(start: int, length: int = 8) -> tuple[list[int], list[int]]:
    """n³ + start"""
    seq = [start + i * i * i for i in range(length)]
    return seq, [seq[6], seq[7]]


def powers_of(base: int, start_exp: int, length: int = 8) -> tuple[list[int], list[int]]:
    """base^exp, base^(exp+1), ..."""
    seq = [base ** (start_exp + i) for i in range(length)]
    return seq, [seq[6], seq[7]]


# ═══════════════════════════════════════════════════════════════════════════
# Pattern registry
# ═══════════════════════════════════════════════════════════════════════════

PATTERN_DEFS = [
    # (name, generator_fn, weight, explanation_template)
    ("Arithmetische Folge", "arith", 15, "Konstante Differenz +{diff}"),
    ("Geometrische Folge", "geom", 10, "Konstanter Faktor ×{ratio}"),
    ("Alternierende Folge", "alt", 10, "+{add}, ×{mul} im Wechsel"),
    ("Quadratzahlen", "quad", 8, "n² + {start}"),
    ("Fibonacci-artig", "fib", 10, "Jedes Glied = Summe der beiden Vorgänger"),
    ("Verschachtelte Folgen", "inter", 10, "Zwei Folgen verschränkt: +{d1} und +{d2}"),
    ("Differenzenwachstum", "diffgr", 8, "Differenz wächst um +{growth} je Schritt"),
    ("Primzahlen", "prime", 6, "Primzahlen ab der {skip}. Primzahl"),
    ("Multiplikativ alternierend", "multalt", 6, "×{mul1}, ×{mul2} im Wechsel"),
    ("Ziffernumkehr", "digrev", 4, "Ziffern umdrehen, dann +{add}"),
    ("Kubikzahlen", "cubic", 5, "n³ + {start}"),
    ("Potenzen", "pow", 8, "{base}ⁿ ab n={start_exp}"),
]


def _generate_pattern(key: str) -> tuple[list[int], list[int], str]:
    """Generate a sequence from the named pattern with random parameters."""
    match key:
        case "arith":
            start = random.randint(-20, 50)
            diff = random.choice([d for d in range(-15, 16) if d != 0])
            seq, nxt = arithmetic(start, diff)
            return seq, nxt, f"Konstante Differenz +{diff}"
        case "geom":
            start = random.choice([1, 2, 3, -2, -3, 5])
            ratio = random.choice([2, 3, -2, -3])
            seq, nxt = geometric(start, ratio)
            return seq, nxt, f"Konstanter Faktor ×{ratio}"
        case "alt":
            start = random.randint(1, 20)
            add = random.choice([1, 2, 3, 4, 5, -1, -2, -3])
            mul = random.choice([2, 3])
            seq, nxt = alternating(start, add, mul)
            return seq, nxt, f"+{add}, ×{mul} im Wechsel"
        case "quad":
            start = random.randint(0, 20)
            seq, nxt = quadratic(start)
            return seq, nxt, f"n² + {start}"
        case "fib":
            a = random.randint(1, 20)
            b = random.randint(1, 20)
            seq, nxt = fibonacci_like(a, b)
            return seq, nxt, "Jedes Glied = Summe der beiden Vorgänger"
        case "inter":
            a1 = random.randint(-10, 30)
            d1 = random.choice([d for d in range(-10, 11) if d != 0])
            a2 = random.randint(-10, 30)
            d2 = random.choice([d for d in range(-10, 11) if d != 0 and d != d1])
            seq, nxt = interleaved(a1, d1, a2, d2)
            return seq, nxt, f"Zwei Folgen verschränkt: +{d1} und +{d2}"
        case "diffgr":
            start = random.randint(-10, 30)
            diff = random.choice([1, 2, 3, 4, 5])
            growth = random.choice([1, 2, 3, 4])
            seq, nxt = difference_growth(start, diff, growth)
            return seq, nxt, f"Differenz wächst um +{growth} je Schritt"
        case "prime":
            skip = random.randint(0, 30)
            seq, nxt = prime_sequence(skip)
            return seq, nxt, f"Primzahlen ab der {skip + 1}. Primzahl"
        case "multalt":
            start = random.choice([1, 2, 3])
            mul1 = random.choice([2, 3])
            mul2 = random.choice([2, 3])
            seq, nxt = multiplicative_alternating(start, mul1, mul2)
            return seq, nxt, f"×{mul1}, ×{mul2} im Wechsel"
        case "digrev":
            start = random.randint(10, 99)
            add = random.choice([1, 2, 3, 5, 7, 9])
            seq, nxt = digit_reverse(start, add)
            return seq, nxt, f"Ziffern umdrehen, dann +{add}"
        case "cubic":
            start = random.randint(-5, 10)
            seq, nxt = cubic(start)
            return seq, nxt, f"n³ + {start}"
        case "pow":
            base = random.choice([2, 3, 4, 5])
            start_exp = random.randint(0, 4)
            seq, nxt = powers_of(base, start_exp)
            return seq, nxt, f"{base}ⁿ ab n={start_exp}"
        case _:
            return arithmetic(1, 1), [1, 1], "Fallback"


def _pick_pattern() -> tuple[str, float]:
    """Choose a pattern by weight. Returns (key, weight)."""
    total = sum(p[2] for p in PATTERN_DEFS)
    r = random.uniform(0, total)
    acc = 0.0
    for _name, key, weight, _tmpl in PATTERN_DEFS:
        acc += weight
        if r <= acc:
            return key, weight
    return PATTERN_DEFS[-1][1], PATTERN_DEFS[-1][2]


# ═══════════════════════════════════════════════════════════════════════════
# Distractor generation
# ═══════════════════════════════════════════════════════════════════════════

def _make_distractors(correct: list[int], seq: list[int]) -> list[list[int]]:
    """Generate 3 wrong answer pairs that look plausible."""
    v1, v2 = correct
    distractors: set[tuple[int, int]] = set()

    # Common error: swap order
    if v1 != v2:
        distractors.add((v2, v1))

    # Off-by variations
    for dv1 in [-2, -1, 1, 2]:
        for dv2 in [-2, -1, 1, 2]:
            distractors.add((v1 + dv1, v2 + dv2))

    # Pattern-specific wrong answers
    last = seq[-1]
    diffs = [seq[i + 1] - seq[i] for i in range(len(seq) - 1)]
    avg_diff = sum(diffs) // len(diffs) if diffs else 1

    # Extrapolate with wrong operation
    distractors.add((last + avg_diff, last + 2 * avg_diff))
    distractors.add((last * 2, last * 2 + avg_diff))
    distractors.add((v1 + avg_diff, v2 + avg_diff))

    # Remove correct answer and implausible entries
    distractors.discard((v1, v2))
    distractors = {
        d for d in distractors
        if d[0] != d[1] or abs(d[0]) < 10_000_000
    }

    chosen = random.sample(sorted(distractors), min(3, len(distractors)))
    return [[c[0], c[1]] for c in chosen]


# ═══════════════════════════════════════════════════════════════════════════
# Question assembly
# ═══════════════════════════════════════════════════════════════════════════

def generate_one(seed: int | None = None) -> dict:
    """Generate a single Zahlenfolgen exercise."""
    if seed is not None:
        random.seed(seed)

    pattern_key, _ = _pick_pattern()
    seq, next_terms, explanation = _generate_pattern(pattern_key)

    # Show 6 numbers + "? ?"
    visible = seq[:6]
    correct_pair = next_terms

    # Create options
    distractors = _make_distractors(correct_pair, visible)
    all_options = [correct_pair] + distractors
    random.shuffle(all_options)

    # Find correct answer index
    correct_idx = next(
        i for i, opt in enumerate(all_options) if opt == correct_pair
    )

    # Append E option
    options: list[tuple[int, ...] | str] = [tuple(o) for o in all_options] + ["none"]

    answer_letter = ["A", "B", "C", "D", "E"][correct_idx]
    correct_str = f"{correct_pair[0]}/{correct_pair[1]}"

    return {
        "sequence": " ".join(str(x) for x in visible),
        "correct_pair": correct_pair,
        "correct_str": correct_str,
        "options": options,
        "answer_letter": answer_letter,
        "correct_idx": correct_idx,
        "explanation": explanation,
    }


def format_question(ex: dict) -> str:
    """Format a Zahlenfolgen exercise as question text."""
    lines = [f"Zahlenfolge: {ex['sequence']} ? ?", ""]
    letters = ["A", "B", "C", "D", "E"]
    for i, opt in enumerate(ex["options"]):
        letter = letters[i]
        if opt == "none":
            lines.append(f"{letter}) Keine der Antworten ist richtig")
        else:
            lines.append(f"{letter}) {opt[0]}/{opt[1]}")
    return "\n".join(lines)


def format_solution(ex: dict) -> str:
    """Format the solution text."""
    return f"{ex['answer_letter']} — {ex['correct_str']}\n{ex['explanation']}\n"


def generate_set(count: int, output_dir: Path, start_id: int = 1) -> int:
    """Generate `count` exercises into output_dir with sequential IDs."""
    output_dir.mkdir(parents=True, exist_ok=True)

    for i in range(count):
        qid = start_id + i
        ex = generate_one(seed=qid + 10_000)  # offset seed from implikationen

        q_text = format_question(ex)
        s_text = format_solution(ex)

        (output_dir / f"{qid:04d}_question.txt").write_text(q_text + "\n", encoding="utf-8")
        (output_dir / f"{qid:04d}_solution.txt").write_text(s_text, encoding="utf-8")

    return start_id + count - 1


def main() -> None:
    import argparse

    p = argparse.ArgumentParser(
        description="Generate synthetic Zahlenfolgen exercises"
    )
    p.add_argument("--count", type=int, default=1000, help="Number of exercises")
    p.add_argument("--output", type=Path, required=True, help="Output directory")
    p.add_argument(
        "--start-id", type=int, default=1, help="First question ID (default: 1)"
    )
    args = p.parse_args()

    last_id = generate_set(args.count, args.output, args.start_id)
    print(
        f"Zahlenfolgen: {args.count} exercises generated "
        f"(IDs {args.start_id}–{last_id})"
    )


if __name__ == "__main__":
    main()
