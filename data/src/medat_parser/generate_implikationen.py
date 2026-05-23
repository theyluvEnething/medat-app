"""Generate synthetic Implikationen erkennen exercises.

Produces flat NN_question.txt + NN_solution.txt files that merge seamlessly
with parsed PDF output. IDs continue from the highest existing ID.

Uses abstract letter-codes (like real MedAT: ZS, NZ, ZLI) to force pure
syllogistic reasoning. Premise pairs are weighted so each answer letter
A–E appears roughly 20% of the time, producing a realistic difficulty mix.

Usage: uv run medat-generate-implikationen --count 1000 --output output/implikationen
"""

from __future__ import annotations

import random
from pathlib import Path

# ── Statement types ─────────────────────────────────────────────────────────
# (Premise 1: A→B, Premise 2: B→C)

STATEMENTS = [
    ("Alle {A} sind {B}.", "A ⊂ B"),
    ("Alle {A} sind keine {B}.", "A ∩ B = ∅"),
    ("Einige {A} sind {B}.", "A ∩ B ≠ ∅"),
    ("Einige {A} sind keine {B}.", "A ⊄ B"),
]

CONCLUSION_TEMPLATES = [
    "Alle {A} sind {C}.",
    "Alle {A} sind keine {C}.",
    "Einige {A} sind {C}.",
    "Einige {A} sind keine {C}.",
    "Keine der Schlussfolgerungen ist richtig.",
]

# ── Rule matrix: (premise1_idx, premise2_idx) → conclusion_idx ──────────────
# 0=All-in, 1=All-none, 2=Some-in, 3=Some-none, 4=None-correct

RULE_SET: dict[tuple[int, int], int] = {
    (0, 0): 0,  (0, 1): 1,  (0, 2): 2,  (0, 3): 4,
    (1, 0): 1,  (1, 1): 4,  (1, 2): 4,  (1, 3): 4,
    (2, 0): 2,  (2, 1): 3,  (2, 2): 4,  (2, 3): 4,
    (3, 0): 4,  (3, 1): 4,  (3, 2): 4,  (3, 3): 4,
}

# ── Weighted premise-pair selection ─────────────────────────────────────────
# Each answer letter A–E targets ~20% of exercises for realistic distribution.
# Weights are chosen so the total for each conclusion type is balanced.

_WEIGHTED_PAIRS: list[tuple[int, int, int]] = [
    # Each answer letter A–E targets ~20% of exercises (total weight = 100).
    # → A: Alle A sind C         (target 20)
    (0, 0, 20),
    # → B: Alle A sind keine C   (target 20)
    (0, 1, 10),
    (1, 0, 10),
    # → C: Einige A sind C       (target 20)
    (0, 2, 10),
    (2, 0, 10),
    # → D: Einige A sind keine C (target 20)
    (2, 1, 20),
    # → E: Keine der Schlussfolgerungen ist richtig (target 20, spread across 10 combos)
    (0, 3, 2),
    (1, 1, 2),
    (1, 2, 2),
    (1, 3, 2),
    (2, 2, 2),
    (2, 3, 2),
    (3, 0, 2),
    (3, 1, 2),
    (3, 2, 2),
    (3, 3, 2),
]

_TOTAL_WEIGHT = sum(w for _, _, w in _WEIGHTED_PAIRS)


def _pick_premise_pair() -> tuple[int, int]:
    """Select a premise pair by weight for balanced answer distribution."""
    r = random.uniform(0, _TOTAL_WEIGHT)
    acc = 0.0
    for p1, p2, w in _WEIGHTED_PAIRS:
        acc += w
        if r <= acc:
            return p1, p2
    return _WEIGHTED_PAIRS[-1][0], _WEIGHTED_PAIRS[-1][1]


# ── Abstract letter-code generation ─────────────────────────────────────────
# Real MedAT uses codes like ZS, NZ, ZLI — short uppercase letter combinations
# that carry no semantic meaning, forcing pure logical reasoning.

# Common first letters drawn from the real MedAT pool
_FIRST_LETTERS = list("ABCDEFGHIJKLMNOPRSTUVWZ")
_SECOND_LETTERS = list("ABCDEFGHIJKLMNOPRSTUVWZ")


def _random_code() -> str:
    """Generate a 2- or 3-letter abstract code (e.g. 'ZS', 'XAP', 'BQ')."""
    a = random.choice(_FIRST_LETTERS)
    b = random.choice(_SECOND_LETTERS)
    if random.random() < 0.3:  # 30% are 3-letter codes
        c = random.choice(_SECOND_LETTERS)
        return a + b + c
    return a + b


def _pick_codes() -> tuple[str, str, str]:
    """Return three distinct abstract codes for A, B, C."""
    codes: set[str] = set()
    while len(codes) < 3:
        codes.add(_random_code())
    a, b, c = tuple(codes)  # type: ignore[assignment]
    return a, b, c


# ── Exercise generation ─────────────────────────────────────────────────────


def generate_one(seed: int | None = None) -> dict:
    """Generate a single Implikationen exercise.

    Returns a dict with keys: premises, conclusion_idx, options (shuffled),
    answer_letter, answer_text.
    """
    if seed is not None:
        random.seed(seed)

    p1_idx, p2_idx = _pick_premise_pair()
    conclusion_idx = RULE_SET[(p1_idx, p2_idx)]

    a_code, b_code, c_code = _pick_codes()

    premise1 = STATEMENTS[p1_idx][0].format(A=a_code, B=b_code)
    premise2 = STATEMENTS[p2_idx][0].format(A=b_code, B=c_code)

    concrete = [
        CONCLUSION_TEMPLATES[i].format(A=a_code, C=c_code) for i in range(4)
    ]

    indices = list(range(4))
    random.shuffle(indices)
    shuffled_options = [concrete[i] for i in indices] + [CONCLUSION_TEMPLATES[4]]

    answer_position = 4 if conclusion_idx == 4 else indices.index(conclusion_idx)
    answer_letter = ["A", "B", "C", "D", "E"][answer_position]

    return {
        "premise1": premise1,
        "premise2": premise2,
        "premise_types": (p1_idx, p2_idx),
        "conclusion_idx": conclusion_idx,
        "options": shuffled_options,
        "answer_letter": answer_letter,
        "answer_text": shuffled_options[answer_position],
    }


def format_question(ex: dict) -> str:
    """Format a generated exercise as a question text block."""
    lines = ["Prämissen:"]
    lines.append(f"- {ex['premise1']}")
    lines.append(f"- {ex['premise2']}")
    lines.append("")
    for i, opt in enumerate(ex["options"]):
        letter = ["A", "B", "C", "D", "E"][i]
        lines.append(f"{letter}) {opt}")
    return "\n".join(lines)


def format_solution(ex: dict) -> str:
    """Format the solution text."""
    return f"{ex['answer_letter']}\n"


def generate_set(count: int, output_dir: Path, start_id: int = 1) -> int:
    """Generate `count` exercises into output_dir with sequential IDs."""
    output_dir.mkdir(parents=True, exist_ok=True)

    for i in range(count):
        qid = start_id + i
        ex = generate_one(seed=qid)

        q_text = format_question(ex)
        s_text = format_solution(ex)

        (output_dir / f"{qid:04d}_question.txt").write_text(
            q_text + "\n", encoding="utf-8"
        )
        (output_dir / f"{qid:04d}_solution.txt").write_text(s_text, encoding="utf-8")

    return start_id + count - 1


def main() -> None:
    import argparse

    p = argparse.ArgumentParser(
        description="Generate synthetic Implikationen erkennen exercises"
    )
    p.add_argument("--count", type=int, default=1000, help="Number of exercises")
    p.add_argument("--output", type=Path, required=True, help="Output directory")
    p.add_argument(
        "--start-id", type=int, default=1, help="First question ID (default: 1)"
    )
    args = p.parse_args()

    last_id = generate_set(args.count, args.output, args.start_id)
    print(
        f"Implikationen: {args.count} exercises generated "
        f"(IDs {args.start_id}–{last_id})"
    )


if __name__ == "__main__":
    main()
