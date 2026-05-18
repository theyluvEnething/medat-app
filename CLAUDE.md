# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Medat study app — an Electron desktop app for practising the KFF (Kognitive Fähigkeiten und Fertigkeiten) test of the Austrian MedAT entrance exam. The `data/` directory contains Python tooling to extract questions from PDFs into structured JSON. The `app/` directory is the Electron + React + TypeScript frontend that runs timed KFF test simulations.

## Commands

### App (`app/`)

```bash
cd app
npm install
npm run dev          # Start Electron dev with HMR
npm run build        # Production build
npm run preview      # Preview production build
npm run typecheck    # tsc --noEmit across all tsconfigs
npm run lint         # oxlint
npm run format       # oxfmt
```

### Data (`data/`)

```bash
cd data
uv run pytest -q     # Run parser tests
uv run ruff check .  # Lint
uv run ruff format . # Format
uv run ty check      # Type-check
```

## Architecture

### KFF test flow (hard timing constraints match the real exam)

The test runs 6 sequential sections with fixed time limits:

| # | Section | Time | Questions |
|---|---------|------|-----------|
| 1 | Figuren zusammensetzen | 20 min | 15 |
| 2 | Ausweise Merken (memorize) | 8 min | 25 items shown |
| 3 | Zahlenfolgen | 15 min | 10 |
| 4 | Wortflüssigkeit | 20 min | 15 |
| 5 | Ausweise Merken (recall) | — | 25 questions |
| 6 | Implikationen erkennen | 10 min | 10 |

Sections 2 and 5 are paired: section 2 displays 25 allergy-pass-like items for memorization; section 5 quizzes recall. Section 5 has no separate timer — the exam gives a fixed time for the recall phase, but in practice users answer the 25 questions within the post-Wortflüssigkeit buffer. This app auto-advances all other sections when time expires.

### Data layer

Questions are extracted from PDFs into structured JSON + images under `data/output/`. Full data format documentation: [`data/DATA_FORMAT.md`](data/DATA_FORMAT.md).

Four section parsers are implemented:

| Parser | Script | Output |
|--------|--------|--------|
| Implikationen erkennen | `implikationen_parser.py` | 70 questions (7×10) |
| Wortflüssigkeit | `wortfluessigkeit_parser.py` | 1500 questions (100×15) |
| Zahlenfolgen | `zahlenfolgen_parser.py` | 70 questions (7×10) |
| Figuren zusammensetzen | `figuren_parser.py` | 105 questions (7×15) + cropped PNG images |

Each question is stored as an individual JSON file indexed by global ID, grouped into set directories. Answer keys are in `answers.json` per section.

Run all parsers:
```bash
cd data
python -m medat_parser.pdf_parser --input . --output output/
```

Or a single section:
```bash
python -m medat_parser.implikationen_parser --input "Implikationen erkennen-120325-Studenten.pdf" --output output/implikationen/
```

Ausweise Merken is not yet implemented (pending).

### App component tree

```
App
├── Home                    # Landing page, test start button
└── Test                    # Orchestrates the full KFF run
    ├── SectionTimer        # Countdown + auto-advance
    ├── QuestionCard        # Renders question stem + A–E buttons
    │   ├── FigurenRenderer # SVG/image for Figuren section
    │   └── AusweiseGrid    # 5×5 grid for memorization phase
    └── Results             # Score summary after all sections
```

State machine per section: `waiting` → `active` → `finished`. The Test page owns a `currentSectionIndex` and advances on timer expiry or manual submission (where allowed). Answers are recorded into a `Map<questionId, choice>` and scored against the JSON answer key at the end.

### Key design decisions

- **Electron, not web**: the real MedAT is offline; the app must work without a network. Electron also simplifies file access for question JSON and images.
- **No router**: the app has exactly two screens (Home and Test). React state switches between them; no react-router dependency.
- **Questions are static assets**: the JSON is imported/bundled at build time, not fetched. This keeps the app fully offline and fast.
- **Tailwind v4**: uses the Vite plugin (`@tailwindcss/vite`) with CSS-based config (`@import "tailwindcss"`). No `tailwind.config.ts`.
- **electron-vite**: handles main/preload/renderer builds in one config. Output goes to `out/`.

### Adding new question sets

1. Place new PDFs in `data/` (alongside existing ones)
2. Run `python -m medat_parser.pdf_parser --input . --output output/` from `data/`
3. Copy the relevant set directories from `data/output/<section>/sets/set_XX/` into the app assets
4. The app picks up new questions on next build
