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

The converter script names images by global question ID: `{id}.png` padded to 3 digits for figuren, or uses the `image` field from parser output for ausweise cards.

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

All parsers in `data/src/medat_parser/`:

| Parser | Input | Output |
|--------|-------|--------|
| `figuren_parser.py` | PDF | JSON + cropped PNGs per question |
| `implikationen_parser.py` | PDF | JSON with premises + conclusions |
| `wortfluessigkeit_parser.py` | PDF | JSON with letter sequences + options |
| `zahlenfolgen_parser.py` | PDF | JSON with number sequences + options |
| `ausweise_parser.py` | PDF | JSON for memorize cards + recall questions + card PNGs |
| `pdf_parser.py` | All PDFs | Dispatches to section parsers |

### Parser output structure

```
data/output/<section>/
  answers.json       # {qid: answer_letter, ...}
  sets/
    set_01/
      001.json       # Per-question JSON (global ID)
      001.png        # Image (figuren + ausweise only)
```

Each question JSON has a global `id`, `set` number, `set_index` (1-based within set), and `answer`. See `data/DATA_FORMAT.md` for per-section schemas.

### Converter (`converter.py`)

Reads parser output from `output/<section>/sets/` and produces a flat `Record<section, Question[]>` JSON file at `app/src/renderer/src/assets/questions.json`.

For each section, `generate_content()` flattens the rich parser fields into a single `content` string (with `\n` line breaks for options). The `image` field is preserved for ausweise_memorize cards.

Run after any parser changes:
```bash
cd data
uv run medat-convert --input output --output ../app/src/renderer/src/assets/questions.json
```

### Adding a new question set

1. Place PDFs in `data/input/<section>/`
2. Parse: `uv run medat-parse --input input/ --output output/`
3. Convert: `uv run medat-convert --input output --output ../app/src/renderer/src/assets/questions.json`
4. Copy images: `cp data/output/<section>/sets/set_*/*.png app/src/renderer/src/assets/<section>/`
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
# then copy any new images
cp data/output/figuren/sets/set_*/*.png app/src/renderer/src/assets/figuren/
cp data/output/ausweise/images/*.png app/src/renderer/src/assets/ausweise/
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
