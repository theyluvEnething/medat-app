# Data Format

Parsed MedAT KFF questions are stored as flat text files under `output/<section>/`.
Each question has exactly two files: `NN_question.txt` and `NN_solution.txt`, plus
an optional image file (`NN_question.png`) for visual sections.

## Design principles

- **Flat, not nested** — no `sets/set_01/` subdirectories; all questions in a section
  live in the same directory, named by global ID
- **Plain text, not JSON** — questions and solutions are human-readable `.txt` files
- **One question = two files** — `_question.txt` + `_solution.txt`; images use `_question.png`
- **Zero-padded IDs** — padding matches the maximum question count in that section

## Directory layout

```
output/
  figuren/
    001_question.png       # Cropped figure (255 questions, 3-digit IDs)
    001_question.txt
    001_solution.txt
    ...
    255_question.png
    255_question.txt
    255_solution.txt
    solutions/
      page_37.png          # Rendered answer-key pages
      ...

  implikationen/
    01_question.txt        # 70 questions, 2-digit IDs
    01_solution.txt
    ...
    70_question.txt
    70_solution.txt

  wortfluessigkeit/
    0001_question.txt      # 1650 questions, 4-digit IDs
    0001_solution.txt
    ...
    1650_question.txt
    1650_solution.txt

  zahlenfolgen/
    01_question.txt        # 70 questions, 2-digit IDs
    01_solution.txt
    ...
    70_question.txt
    70_solution.txt

  ausweise/
    cards/                 # 320 memorization cards, 3-digit IDs
      001_question.png     #   Card image (rendered Ausweis)
      001_question.txt     #   Card field data
      ...
      320_question.png
      320_question.txt
    recall/                # 1000 recall questions, 4-digit IDs
      0001_question.txt
      0001_solution.txt
      ...
      1000_question.txt
      1000_solution.txt
```

## File formats

### `_question.txt` — the question as displayed to the user

Each section has a specific format optimized for rendering in the Electron app.

#### Figuren zusammensetzen

```
Figuren zusammensetzen
Frage 1
```

Minimal — the question is the image (`001_question.png`). The A–E answer buttons are
always shown by the app for this section.

#### Implikationen erkennen

```
Prämissen:
- Alle A sind B.
- Kein B ist C.

A) Alle A sind C.
B) Kein A ist C.
C) Einige A sind C.
D) Einige A sind nicht C.
E) Keine der Schlussfolgerungen ist richtig.
```

Premises as bullet points, then A–E conclusions one per line.

#### Wortflüssigkeit

```
Buchstabenreihe: H U E A R E F

A) U
B) F
C) E
D) R
E) Keine der Antworten ist richtig.
```

Letter sequence followed by A–E options.

#### Zahlenfolgen

```
Zahlenfolge: 23 -4 28 19 24 47 43 ? ?

A) 58/99
B) 66/82
C) 71/90
D) 76/90
E) Keine der Antworten ist richtig.
```

Number sequence followed by A–E options.

#### Ausweise Merken — Cards (`ausweise/cards/`)

```
Name: GILTONS
Geburtstag: 22. März
Medikamenteneinnahme: Nein
Blutgruppe: B
Bekannte Allergien: Pistazien, Meerschweinchen
Ausweisnummer: 93115
Ausstellungsland: Grenada
```

Key-value field listing. Paired with `NN_question.png` (the rendered card image).
No solution file — cards are memorization items, not answerable questions.

#### Ausweise Merken — Recall (`ausweise/recall/`)

```
Wie lautet die Ausweisnummer der Person mit dem Namen UMSHAU?

A) 81942
B) 23612
C) 68213
D) 32771
E) Keine der Antworten ist richtig.
```

Question text followed by A–E options.

### `_solution.txt` — the correct answer

One line containing the answer letter and optional auxiliary data.

**Figuren:**
```
C
```

**Implikationen:**
```
D
```

**Wortflüssigkeit:**
```
C — EHEFRAU
```
Format: `<letter> — <word>`

**Zahlenfolgen:**
```
C — 71/90
A₄=A₂+A₁, A₅=A₃+A₂, A₆=A₄+A₃, ...
```
Format: `<letter> — <value>` followed by explanation on subsequent lines.

**Ausweise Recall:**
```
E
```

### `_question.png` — visual question content

- **Figuren**: Cropped figure composition puzzle, 200 DPI PNG
- **Ausweise Cards**: Cropped ID card image, 200 DPI PNG

### `solutions/` directory (Figuren only)

Full-page renders of the PDF answer-key pages. Referenced by the app to show which
pieces formed the correct figure. Named `page_NN.png` matching the original PDF page
numbers.

## Question counts and ID padding

| Section | Dir | Count | Per Set | Padding | ID Range |
|---------|-----|-------|---------|---------|----------|
| Figuren | `figuren/` | 255 | 15 | 3-digit | 001–255 |
| Implikationen | `implikationen/` | 1,070 | 10 | 4-digit | 0001–1070 |
| Wortflüssigkeit | `wortfluessigkeit/` | 1,650 | 15 | 4-digit | 0001–1650 |
| Zahlenfolgen | `zahlenfolgen/` | 1,070 | 10 | 4-digit | 0001–1070 |
| Ausweise Cards | `ausweise/cards/` | 320 | 8 | 3-digit | 001–320 |
| Ausweise Recall | `ausweise/recall/` | 1,000 | 25 | 4-digit | 0001–1000 |

## Set membership

Sets are derived from global IDs, not stored in the file structure:

| Section | Set formula | Set index formula |
|---------|-------------|-------------------|
| Figuren | `(id-1) // 15 + 1` | `(id-1) % 15 + 1` |
| Implikationen | `(id-1) // 10 + 1` | `(id-1) % 10 + 1` |
| Wortflüssigkeit | `(id-1) // 15 + 1` | `(id-1) % 15 + 1` |
| Zahlenfolgen | `(id-1) // 10 + 1` | `(id-1) % 10 + 1` |
| Ausweise Cards | `(id-1) // 8 + 1` | `(id-1) % 8 + 1` |
| Ausweise Recall | `(id-1) // 25 + 1` | `(id-1) % 25 + 1` |

## Selecting questions for a test

1. Pick a set number S for each section.
2. Compute the ID range: `(S-1)*count + 1` to `S*count`.
3. Read `_question.txt` and `_question.png` (if present) for each ID.
4. Read `_solution.txt` to get the answer letter.

Example: Figuren Set 3 → IDs 31–45 → read `031_question.png`, `031_question.txt`,
`031_solution.txt` through `045_*`.

## Adding new questions

1. Place new PDFs in `input/<section>/`.
2. Run `uv run medat-parse --input input/ --output output/`.
3. IDs are auto-assigned continuing from the highest existing ID.
4. Copy any new images to the app: `cp output/<section>/*.png ../app/src/renderer/src/assets/<section>/`.
5. Run `uv run medat-convert --input output --output ../app/src/renderer/src/assets/questions.json`.
