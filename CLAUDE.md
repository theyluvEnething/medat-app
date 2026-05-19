# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

## Project overview

MedAT KFF Trainer — an offline Electron desktop app for practising the KFF (Kognitive Fähigkeiten und Fertigkeiten) test of the Austrian MedAT entrance exam.

- **`app/`** — Electron + Vite + React 19 + TypeScript + Tailwind v4 frontend
- **`data/`** — Python tooling (3.13, uv) to extract questions from PDFs into structured JSON

## Commands

### App (`app/`)

```bash
cd app
npm install           # install deps (Node ≥ 22)
npm run dev           # Electron dev with HMR at localhost:5173
npm run build         # production build → out/
npm run preview       # preview production build
npm run typecheck     # tsc --noEmit across all three tsconfigs
npm run lint          # oxlint
npm run format        # oxfmt
```

### Data (`data/`)

```bash
cd data
uv run pytest -q             # parser tests
uv run ruff check .          # lint
uv run ruff format .         # format
uv run ty check              # type-check

# Run all parsers on input PDFs
uv run medat-parse --input input/ --output output/

# Regenerate the app's question bundle after parsing
uv run medat-convert --input output --output ../app/src/renderer/src/assets/questions.json

# Merge question sets from different PDF runs
uv run medat-merge --input output/ --output merged/
```

## Architecture

### Screen routing

App.tsx manages a `Screen` enum: `'login'` → `'home'` → (`'test'` | `'settings'`). No router library — just React state switches.

```
App
├── Login           # Username input, pre-filled from localStorage
├── Home            # Progress dashboard, start/settings buttons
├── Test            # Full 6-section KFF simulation
│   ├── HintBanner  # "Notizen VERBOTEN" for figuren + ausweise_memorize
│   ├── Timer       # Progress bar + M:SS countdown
│   └── QuestionCard # Content + A–E buttons (images for figuren/ausweise)
└── Settings        # Per-section set index override + reset
```

### Test flow

The test runs 6 sequential sections. State machine per section: `intro` → `active` → `section-done`. After the last section, `results` shows correct/total score.

| # | Section key | Label | Time | Per Set |
|---|-------------|-------|------|---------|
| 1 | `figuren` | Figuren zusammensetzen | 20 min | 15 |
| 2 | `ausweise_memorize` | Ausweise Merken — Einprägen | 8 min | 8 |
| 3 | `wortfluessigkeit` | Wortflüssigkeit | 20 min | 15 |
| 4 | `zahlenfolgen` | Zahlenfolgen | 15 min | 10 |
| 5 | `ausweise_recall` | Ausweise Merken — Abfrage | 8 min | 25 |
| 6 | `implikationen` | Implikationen erkennen | 10 min | 10 |

Defined in `types.ts` as `SECTION_ORDER: SectionConfig[]`. The `count` field is the set size used for set-based progress tracking and question selection.

### Question selection (set-based)

Each section has a pool of questions (`questions.json`), divided into sets of `count` questions each. The current set is tracked in `SectionProgress.currentSetIndex`.

`Test.tsx:selectQuestions()` — the core algorithm:
1. Read pool segment `[setIndex * count .. (setIndex + 1) * count]`
2. Filter out questions whose IDs are in `progress.completed` (already answered correctly)
3. If filtered list is empty → all questions in set are done → advance `currentSetIndex` (wrap to 0 if past the end)
4. If filtered list is shorter than `count` → fill with non-completed wrong answers from the same set
5. Return the final list

The `useMemo` that calls `selectQuestions` also persists the new `currentSetIndex` if the set changed (detected by checking which set the first returned question belongs to).

### Progress persistence

`storage.ts` wraps `localStorage` with JSON serialization. Keys:
- `medat_last_user` → last username string
- `medat_users` → `Record<string, UserProgress>` where `UserProgress.sections` maps each `SectionKey` to `SectionProgress { currentSetIndex, completed[], wrongIds[] }`

Progress is saved by `Test.tsx:persistSectionProgress()` only when a section transitions (timer expiry or manual advance). The "Abbrechen" button exits without calling this function, so no progress is saved.

When all questions in a set are in `completed`, `currentSetIndex` increments. When all sets for a section are done, the index wraps to 0.

### QuestionCard rendering by section

`QuestionCard.tsx` renders differently per section:
- **figuren**: Image from `assets/figuren/{id}.png` via `import.meta.glob`, max 60vh height
- **ausweise_memorize**: Pass image from `assets/ausweise/{image}.png` via `import.meta.glob`, then field text below. No A–E buttons (memorization phase).
- **All others**: Text content with `whitespace-pre-line` + A–E answer grid
- Selected answer highlighted in emerald

If a glob lookup fails (image not found), shows "Bild nicht verfügbar" fallback.

### Image handling

Images are in `app/src/renderer/src/assets/<section>/` and loaded via Vite's `import.meta.glob` with `{ eager: true }`. This bundles images through Vite's asset pipeline at build time. The glob returns `Record<string, { default: string }>` where the key is the relative path and `default` is the hashed URL.

The converter script produces image references as `{id}.png` padded to 3 digits. Data files use `NNN_question.png` naming; the copy step strips the `_question` suffix for app compatibility.

### Electron setup

- **Main** (`main/index.ts`): Creates BrowserWindow (1280×720, min 900×600, no fullscreen, sandbox: false). Loads from `ELECTRON_RENDERER_URL` in dev or `out/renderer/index.html` in prod.
- **Preload** (`preload/index.ts`): Minimal contextBridge exposing only a `ping` IPC stub. No real IPC needed since the app uses localStorage for persistence.
- **Build**: `electron-vite` handles three targets (main/preload/renderer) in one config. `externalizeDepsPlugin()` on main + preload.

### TypeScript config

Three tsconfigs with project references:
- `tsconfig.json` — root, strict, references the other two
- `tsconfig.node.json` — main process + preload, `composite: true`, outputs to `out/main/`
- `tsconfig.web.json` — renderer, `composite: true`, `resolveJsonModule: true`, outputs to `out/renderer/`

`vite-env.d.ts` references `vite/client` for `import.meta.glob` types.

## Data pipeline

### Parser scripts

All parsers in `data/src/medat_parser/` extract questions from PDFs and write flat
text files — no JSON, no nested `sets/` directories.

| Parser | Output |
|--------|--------|
| `figuren_parser.py` | `NNN_question.png` + `NNN_question.txt` + `NNN_solution.txt` + `solutions/` |
| `implikationen_parser.py` | `NN_question.txt` + `NN_solution.txt` |
| `wortfluessigkeit_parser.py` | `NNNN_question.txt` + `NNNN_solution.txt` |
| `zahlenfolgen_parser.py` | `NN_question.txt` + `NN_solution.txt` |
| `ausweise_parser.py` | `cards/NNN_question.png` + `cards/NNN_question.txt` + `recall/NNNN_question.txt` + `recall/NNNN_solution.txt` |
| `extract_ausweise_images.py` | `recall/NNNN_question.png` — cropped question blocks with embedded face photos |
| `pdf_parser.py` | Dispatches to section parsers |
| `merge.py` | Parses new PDFs with ID remapping; merges into existing output |
| `converter.py` | Reads flat output → app's `questions.json` |

### Parser output structure (flat text, no JSON)

Each question is two or three flat files in a section directory:

```
data/output/
  figuren/                  # 255 questions, 3-digit IDs
    001_question.png        #   Cropped figure image
    001_question.txt        #   "Figuren zusammensetzen\nFrage 1"
    001_solution.txt        #   "C"
    solutions/
      page_37.png ...       #   Full-page answer-key renders
  implikationen/            # 70 questions, 2-digit IDs
    01_question.txt         #   Prämissen: ... \nA) ... E)
    01_solution.txt         #   "D"
  wortfluessigkeit/         # 1650 questions, 4-digit IDs
    0001_question.txt       #   Buchstabenreihe: ... \nA) ... E)
    0001_solution.txt       #   "C — EHEFRAU"
  zahlenfolgen/             # 70 questions, 2-digit IDs
    01_question.txt         #   Zahlenfolge: ... \nA) ... E)
    01_solution.txt         #   "C — 71/90\nexplanation..."
  ausweise/
    cards/                  # 320 memorization cards, 3-digit IDs
      001_question.png      #   Cropped Ausweis image
      001_question.txt      #   "Name: GILTONS\nGeburtstag: ..."
    recall/                 # 1000 recall questions, 4-digit IDs
      0001_question.txt     #   "Wie lautet...\nA) ... E)"
      0001_question.png     #   Cropped question block (may include face photo)
      0001_solution.txt     #   "E"
```

Each `_question.txt` file contains exactly what the app displays — premises,
options, sequences already formatted with newlines. Each `_solution.txt` contains
the answer letter and any auxiliary data (correct word, explanation).

Full schema and question counts are in `data/DATA_FORMAT.md`.

### Converter (`converter.py`)

Reads the flat output directory and produces `app/src/renderer/src/assets/questions.json`.
The converter:

1. Scans each section directory for `*_question.txt` files
2. Extracts the answer from `*_solution.txt` (first line, first character before ` — `)
3. For ausweise_cards, reads the `image` field from matching PNGs

Run after any parser changes:
```bash
cd data
uv run medat-convert --input output --output ../app/src/renderer/src/assets/questions.json
```

### Adding a new question set

1. Place PDFs in `data/input/<section>/`
2. Parse: `uv run medat-parse --input input/ --output output/`
3. Convert: `uv run medat-convert --input output --output ../app/src/renderer/src/assets/questions.json`
4. Copy images (strip `_question` suffix for app compat):
   ```bash
   for f in data/output/figuren/*_question.png; do
       base=$(basename "$f" _question.png)
       cp "$f" "app/src/renderer/src/assets/figuren/${base}.png"
   done
   for f in data/output/ausweise/cards/*_question.png; do
       base=$(basename "$f" _question.png)
       cp "$f" "app/src/renderer/src/assets/ausweise/${base}.png"
   done
   cp data/output/figuren/solutions/*.png app/src/renderer/src/assets/solutions/
   ```
5. Rebuild app: `cd app && npm run dev`

## Key design decisions

- **Electron, not web**: MedAT is offline; app must work without network. Electron simplifies file access.
- **No router**: Only 4 screens; React state switches between them.
- **localStorage, not IPC**: User progress stored in localStorage (persisted by Electron's Chromium). Avoids IPC complexity for data that only the renderer touches.
- **Questions as static imports**: `questions.json` is imported at build time, not fetched. Keeps the app offline and fast.
- **Set-based progress**: Progress tracked per set (not flat index). Questions drawn from the current set; correct answers skipped in future sessions. This matches how the real MedAT is structured (distinct question sets).
- **Abbrechen = no save**: Only the "Nächster Abschnitt" / timer-expiry path calls `persistSectionProgress`. This means the user can experiment without polluting their stats.
- **Tailwind v4**: Uses Vite plugin with CSS-based config (`@import "tailwindcss"`). No `tailwind.config.ts`.
- **electron-vite**: Single config for main/preload/renderer. Output goes to `out/`.
- **No external state library**: React `useState` + localStorage is sufficient for this app's needs.

## Common tasks

### Regenerating question data after parser changes

```bash
cd data
uv run medat-convert --input output --output ../app/src/renderer/src/assets/questions.json
# Copy images to app (strip _question suffix)
for f in output/figuren/*_question.png; do
    base=$(basename "$f" _question.png)
    cp "$f" "../app/src/renderer/src/assets/figuren/${base}.png"
done
for f in output/ausweise/cards/*_question.png; do
    base=$(basename "$f" _question.png)
    cp "$f" "../app/src/renderer/src/assets/ausweise/${base}.png"
done
cp output/figuren/solutions/*.png ../app/src/renderer/src/assets/solutions/
```

### Resetting a user's progress

Delete the localStorage keys in Electron DevTools (Ctrl+Shift+I):
```js
localStorage.removeItem('medat_users')
localStorage.removeItem('medat_last_user')
```

### Debugging the renderer

Open Electron DevTools (Ctrl+Shift+I). Check the Console and Application → Local Storage tabs. The Vite dev server also has HMR — React component changes apply instantly.

### Type checking

```bash
cd app
npm run typecheck    # runs tsc --noEmit on all three tsconfigs
```
