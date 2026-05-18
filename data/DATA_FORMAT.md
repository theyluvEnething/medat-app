# Data Format

Parsed MedAT KFF questions are stored under `data/output/<section>/`.

## Directory Structure

```
output/
  implikationen/
    answers.json          # {qid: answer_letter, ...}
    sets/
      set_01/             # Questions 1-10
        001.json
        ...
        010.json
      set_02/             # Questions 11-20
        ...
  wortfluessigkeit/
    answers.json          # {qid: {letter, word}, ...}
    sets/
      set_001/            # Questions 1-15
        0001.json
        ...
      set_100/            # Questions 1486-1500
        ...
  zahlenfolgen/
    answers.json          # {qid: {letter, value, explanation}, ...}
    sets/
      set_01/             # Questions 1-10
        001.json
        ...
  figuren/
    answers.json          # {qid: answer_letter, ...}
    solutions/
      page_37.png         # Solution page for Set 1
      page_38.png         # Solution page for Sets 2-4
      page_39.png         # Solution page for Set 5
      page_40.png         # Solution page for Sets 6-7
    sets/
      set_01/             # Questions 1-15
        001.json
        001.png           # Cropped figure image
        ...
```

## Question JSON Schemas

### Implikationen erkennen

```json
{
  "id": 1,
  "set": 1,
  "set_index": 1,
  "answer": "D",
  "premises": ["EinigeZSsindkeineNZ.", "AlleZLIsindNZ."],
  "conclusions": {
    "A": "AlleZSsindZLI.",
    "B": "AlleZSsindkeineZLI.",
    "C": "EinigeZSsindZLI.",
    "D": "EinigeZSsindkeineZLI.",
    "E": "KeinederSchlussfolgerungenistrichtig."
  }
}
```

### Wortflüssigkeit

```json
{
  "id": 1,
  "set": 1,
  "set_index": 1,
  "answer": "C",
  "answer_word": "EHEFRAU",
  "sequence": "H U E A R E F",
  "options": {"A": "U", "B": "F", "C": "E", "D": "R", "E": "KeinederAntwortenistrichtig"}
}
```

### Zahlenfolgen

```json
{
  "id": 1,
  "set": 1,
  "set_index": 1,
  "answer": "C",
  "answer_value": "71/90",
  "explanation": "A₄=A₂+A₁,A₅=A₃+A₂,A₆=A₄+A₃,...",
  "sequence": "23 -4 28 19 24 47 43 ? ?",
  "options": {
    "A": "58/99",
    "B": "66/82",
    "C": "71/90",
    "D": "76/90",
    "E": "KeinederAntwortenistrichtig"
  }
}
```

### Figuren zusammensetzen

```json
{
  "id": 1,
  "set": 1,
  "set_index": 1,
  "answer": "C",
  "image": "001.png",
  "solution_page": "page_37.png"
}
```

Each question has a corresponding `.png` image (200 DPI, cropped from the rendered PDF page). Solution pages are full-page renders of the answer key pages.

## Question Counts

| Section | Sets | Per Set | Total |
|---------|------|---------|-------|
| Implikationen erkennen | 7 | 10 | 70 |
| Wortflüssigkeit | 100 | 15 | 1500 |
| Zahlenfolgen | 7 | 10 | 70 |
| Figuren zusammensetzen | 7 | 15 | 105 |

## ID Convention

- Global IDs start at 1 and increment sequentially across all sets.
- Implikationen: IDs 1–70 (set = (id-1)//10 + 1, set_index = (id-1)%10 + 1)
- Wortflüssigkeit: IDs 1–1500 (set = (id-1)//15 + 1, set_index = (id-1)%15 + 1)
- Zahlenfolgen: IDs 1–70 (set = (id-1)//10 + 1, set_index = (id-1)%10 + 1)
- Figuren: IDs 1–105 (set = (id-1)//15 + 1, set_index = (id-1)%15 + 1)

## Selecting Questions for a Test

To build a test with 15 Figuren, 15 Wortflüssigkeit, 10 Implikationen, and 10 Zahlenfolgen:

1. Pick a set number for each section (e.g., set 3 for Figuren).
2. Read all JSON files from `sets/set_03/` of that section.
3. For Figuren, also load the `.png` image referenced by each JSON.
4. The answer key is embedded in each question JSON (`answer` field).
