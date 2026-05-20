# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

## Project overview

MedAT KFF Trainer — an offline Electron desktop app and web app for practising the KFF (Kognitive Fähigkeiten und Fertigkeiten) test of the Austrian MedAT entrance exam.

- **`app/`** — Electron + Vite + React 19 + TypeScript + Tailwind v4 frontend (shared renderer code)
- **`web/`** — Standalone Vite web build importing renderer source from `app/` via `@app` alias
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

### Web (`web/`)

```bash
cd web
npm install           # install deps (Node ≥ 22)
npm run dev           # Vite dev server at localhost:5173
npm run build         # tsc + vite build → dist/
npm run preview       # preview dist/ at localhost:4173
```

Deployed to GitHub Pages at https://theyluvenething.github.io/medat-app/ (base: `/medat-app/`).

### Data (`data/`)

```bash
cd data
uv run pytest -q             # parser tests
uv run ruff check .          # lint
uv run ruff format .         # format
uv run ty check              # type-check

uv run medat-parse --input input/ --output output/
uv run medat-convert --input output --output ../app/src/renderer/src/assets/questions.json
uv run medat-merge --input output/ --output merged/
```

## Architecture

### Routing

React Router v7 (`HashRouter`) with 7 routes:

```
/ → /login or /home          (redirect based on auth)
/login → Login               Username entry
/home → Home                 Dashboard + gamification stats
/setup → Setup               Full KFF vs single category selection
/session/:type → Session     Active quiz (QuizCard + Timer)
/results → Results           Post-session analytics
/settings → Settings         Per-section set control + reset
/leaderboard → Leaderboard   Supabase-powered global ranking
```

### State management

Zustand v5 store (`store/useAppStore.ts`) with `persist` middleware:
- `user` — username
- `progress` — per-section `SectionProgress` (migrated from old localStorage keys)
- `session` — active quiz state (NOT persisted)
- `sessionHistory` — completed session records (for Results page)
- `gamification` — daily streak, mastery levels (0–100%), wrong-counts tracking

Legacy migration: On first run, the `migrate` callback reads `medat_users` + `medat_last_user` from localStorage and converts them into the new store format.

### Component tree

```
App
├── Login             # Username input, pre-filled from store
├── Home              # Progress dashboard + gamification (streak, mastery)
├── Setup             # Full KFF card + per-category touch cards
├── Session           # Quiz orchestrator (intro → active → section-done)
│   ├── Timer         # Progress bar + M:SS countdown
│   ├── HintBanner    # "Notizen VERBOTEN" for figuren + ausweise_memorize
│   └── QuizCard      # Busuu-style (blue bg, 3D buttons, progress squares)
│       └── ProgressTracker  # Green/red/gray square row at bottom
├── Results           # Score card, per-section bars, wrong answers list
├── Settings          # Colored section cards, −/+ set selector, danger zone
└── Leaderboard       # Supabase-powered ranking table with podium
```

### Test flow

The test runs 6 sequential sections (or a single selected one). State machine per section: `intro` → `active` → `section-done`.

| # | Section key | Label | Time | Per Set |
|---|-------------|-------|------|---------|
| 1 | `figuren` | Figuren zusammensetzen | 20 min | 15 |
| 2 | `ausweise_memorize` | Ausweise Merken — Einprägen | 8 min | 8 |
| 3 | `wortfluessigkeit` | Wortflüssigkeit | 20 min | 15 |
| 4 | `zahlenfolgen` | Zahlenfolgen | 15 min | 10 |
| 5 | `ausweise_recall` | Ausweise Merken — Abfrage | 8 min | 25 |
| 6 | `implikationen` | Implikationen erkennen | 10 min | 10 |

### Question selection (set-based)

`Session.tsx:selectQuestions()` — same algorithm as the old Test.tsx:
1. Read pool segment `[setIndex * count .. (setIndex + 1) * count]`
2. Filter out questions whose IDs are in `progress.completed`
3. If empty → advance `currentSetIndex` (wrap to 0 if past end)
4. If shorter than `count` → fill with non-completed wrong answers from same set
5. Return final list

### QuizCard rendering by section

`QuizCard.tsx` renders differently per section:
- **figuren**: Image from `assets/figuren/{id}.png` via `import.meta.glob`
- **ausweise_memorize**: Image from `assets/ausweise/{image}.png` + field text. No answer buttons.
- **All others**: Large text content + A–E full-width 3D buttons

Design: Bright blue (`bg-blue-600`) background, lighter content card, 3D buttons (`border-b-4`), orange "Weiter" button, progress square row at bottom.

### Image handling

Images in `app/src/renderer/src/assets/<section>/` loaded via Vite's `import.meta.glob` with `{ eager: true }`. Used in QuizCard.tsx for figuren, ausweise, and solution images.

### Persistence

Zustand `persist` middleware (localStorage key: `medat-app-store`). Partialize excludes the active session. Legacy data (`medat_users`, `medat_last_user`) migrated on first load.

### Supabase / Leaderboard

`services/supabase.ts` — client-side Supabase connection using the public anon key.
- `fetchLeaderboard()` — GET all entries sorted by `total_score.desc`
- `upsertUserScore()` — POST with merge-duplicates for upsert

Supabase project: `twjqntyxvpkwbxbyaxzb` (us-east-1). Table: `leaderboard` (id UUID PK, username TEXT UNIQUE, total_score INT, questions_solved INT, questions_correct INT, created_at TIMESTAMPTZ). RLS enabled with public select/insert/update policies.

### Web + Electron dual build

The renderer source in `app/src/renderer/src/` is shared between both targets:
- **Electron**: Built by `electron-vite` (main/preload/renderer)
- **Web**: Built by standalone Vite in `web/`, imports via `@app` alias pointing to `../app/src/renderer/src/`

CSS: `web/src/index.css` uses `@source "../../app/src/renderer/src/**/*.{ts,tsx}"` so Tailwind v4 scans the app source tree. Animations (`pulse-warn`, `fade-in`, `breathe`, `slide-up`) defined in both CSS files.

Vite config uses `resolve.dedupe: ['react', 'react-dom', 'react-router', 'react-router-dom']` to prevent duplicate module instances when app source imports resolve to `app/node_modules/` instead of `web/node_modules/`.

### Electron setup

- **Main** (`main/index.ts`): BrowserWindow 1280×720, sandbox: false
- **Preload** (`preload/index.ts`): Minimal contextBridge (ping stub only)
- **Build**: `electron-vite` with `externalizeDepsPlugin()` on main + preload

### TypeScript config

Three tsconfigs in `app/` with project references:
- `tsconfig.json` — root, strict
- `tsconfig.node.json` — main + preload, composite, → `out/main/`
- `tsconfig.web.json` — renderer, composite, resolveJsonModule, → `out/renderer/`

`web/tsconfig.json` — standalone, includes `../app/src/renderer/src/**/*.{ts,tsx,json}`

## Data pipeline

Parser scripts in `data/src/medat_parser/` extract questions from PDFs into flat text files (no JSON).

| Parser | Output |
|--------|--------|
| `figuren_parser.py` | `NNN_question.png` + `NNN_question.txt` + `NNN_solution.txt` |
| `implikationen_parser.py` | `NNNN_question.txt` + `NNNN_solution.txt` |
| `generate_implikationen.py` | Synthetic implikationen exercises (1000, IDs 71–1070) |
| `wortfluessigkeit_parser.py` | `NNNN_question.txt` + `NNNN_solution.txt` |
| `zahlenfolgen_parser.py` | `NNNN_question.txt` + `NNNN_solution.txt` |
| `generate_zahlenfolgen.py` | Synthetic zahlenfolgen exercises (1000, IDs 71–1070) |
| `ausweise_parser.py` | `cards/NNN_question.png` + `cards/NNN_question.txt` + `recall/NNNN_question.txt` + `recall/NNNN_solution.txt` |
| `converter.py` | Flat output → `questions.json` |
| `merge.py` | Merges new PDF outputs into existing output/ |

### Adding a new question set

1. Place PDFs in `data/input/<section>/`
2. Parse: `uv run medat-parse --input input/ --output output/`
3. Convert: `uv run medat-convert --input output --output ../app/src/renderer/src/assets/questions.json`
4. Copy images (strip `_question` suffix):
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
5. Rebuild: `cd app && npm run dev`

## Key design decisions

- **HashRouter**: Works on both Electron `file://` and web `http://` protocols
- **Zustand persist**: Single localStorage key (`medat-app-store`) with legacy migration from old keys
- **Questions as static imports**: `questions.json` imported at build time, not fetched
- **Set-based progress**: Tracks per-set completion; correct answers skipped in future sessions
- **No backend required**: All persistence is client-side (localStorage + Supabase for leaderboard)
- **Tailwind v4**: `@import "tailwindcss"` with `@source` directive for cross-project scanning
- **dedupe**: Prevents duplicate React/Router instances across `app/node_modules` and `web/node_modules`

## Common tasks

### Regenerating question data

```bash
cd data
uv run medat-convert --input output --output ../app/src/renderer/src/assets/questions.json
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

### Web deployment

```bash
cd web
npm run build          # → dist/
# Deploy dist/ to gh-pages branch:
# (uses git subtree or manual copy to gh-pages orphan branch)
```

### Resetting a user's progress

Via Settings UI (Settings → Gefahrenzone → Alles zurücksetzen), or programmatically:
```js
useAppStore.getState().resetAllProgress()
```

### Type checking

```bash
cd app && npm run typecheck    # all three app tsconfigs
cd web && npx tsc --noEmit     # web tsconfig
```
