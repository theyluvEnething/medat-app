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
  ausweise/
    answers.json          # {qid: answer_letter, ...}
    images/
      001.png ... 320.png # ID card images
    sets/
      set_01/             # Cards 1-8 + recall questions 1-25
        001.json          # Card JSON (fields + image ref)
        q_0001.json       # Recall question JSON
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

### Ausweise Merken (memorize card)

```json
{
  "id": 1,
  "set": 1,
  "set_index": 1,
  "image": "001.png",
  "fields": {
    "Name": "GILTONS",
    "Geburtstag": "22. März",
    "Medikamenteneinnahme": "Nein",
    "Blutgruppe": "B",
    "Bekannte Allergien": "Pistazien, Meerschweinchen",
    "Ausweisnummer": "93115",
    "Ausstellungsland": "Grenada"
  }
}
```

Each card has a corresponding `.png` image showing the full allergy pass. The `fields` map contains the card's structured data.

### Ausweise Merken (recall question)

```json
{
  "id": 1,
  "set": 1,
  "set_index": 1,
  "answer": "E",
  "text": "WielautetdieAusweisnummerderPerson mitdemNamenUMSHAU?",
  "options": {
    "A": "81942",
    "B": "23612",
    "C": "68213",
    "D": "32771",
    "E": "KeinederAntwortenistrichtig"
  }
}
```

Each set has 25 recall questions about the 8 cards in that set. Questions reference card data (names, dates, numbers). One option is always "Keine der Antworten ist richtig".

## Question Counts

| Section | Sets | Per Set | Total |
|---------|------|---------|-------|
| Implikationen erkennen | 7 | 10 | 70 |
| Wortflüssigkeit | 110 | 15 | 1,650 |
| Zahlenfolgen | 7 | 10 | 70 |
| Figuren zusammensetzen | 17 | 15 | 255 |
| Ausweise Merken (memorize) | 40 | 8 | 320 |
| Ausweise Merken (recall) | 40 | 25 | 1,000 |

## ID Convention

- Global IDs start at 1 and increment sequentially across all sets.
- Implikationen: IDs 1–70 (set = (id-1)//10 + 1, set_index = (id-1)%10 + 1)
- Wortflüssigkeit: IDs 1–1650 (set = (id-1)//15 + 1, set_index = (id-1)%15 + 1)
- Zahlenfolgen: IDs 1–70 (set = (id-1)//10 + 1, set_index = (id-1)%10 + 1)
- Figuren: IDs 1–255 (set = (id-1)//15 + 1, set_index = (id-1)%15 + 1)
- Ausweise memorize: IDs 1–320 (set = (id-1)//8 + 1, set_index = (id-1)%8 + 1)
- Ausweise recall: IDs 1–1000 (set = (id-1)//25 + 1, set_index = (id-1)%25 + 1)

## Selecting Questions for a Test

To build a test with 15 Figuren, 15 Wortflüssigkeit, 10 Implikationen, and 10 Zahlenfolgen:

1. Pick a set number for each section (e.g., set 3 for Figuren).
2. Read all JSON files from `sets/set_03/` of that section.
3. For Figuren and Ausweise memorize, also load the `.png` image referenced by each JSON.
4. The answer key is embedded in each question JSON (`answer` field).
