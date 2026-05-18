# MedAT KFF Trainer

Offline desktop app for practising the KFF (Kognitive Fähigkeiten und Fertigkeiten) test of the Austrian MedAT entrance exam. Runs timed full-length simulations matching the real exam — same section order, same time limits, same question counts.

Built with **Electron + Vite + React 19 + TypeScript + Tailwind CSS v4**. Works fully offline.

## Quick start

```bash
cd app
npm install
npm run dev          # starts Electron with HMR at 1280×720
```

Requires **Node ≥ 22**. Use nvm if needed (Node 24 is available in the environment).

## How it works

### Login & user system

On first launch you enter a username. The app creates a persistent profile stored in `localStorage` that tracks every question you answer across all sessions. Your username is remembered for next time.

### Home screen

Shows your overall progress (e.g. "80% — 45/56 richtig") and a per-section breakdown with correct/attempted counts and which set you're on. From here you can:

- **Test starten** — run a full 6-section KFF simulation
- **Einstellungen** — manually set which set you're on for each section (useful if you already completed earlier sets)
- **Abmelden** — switch users

### Test flow

The app runs 6 sequential sections matching the real MedAT KFF:

| # | Section | Time | Per Set |
|---|---------|------|---------|
| 1 | Figuren zusammensetzen | 20 min | 15 questions |
| 2 | Ausweise Merken — Einprägen | 8 min | 8 cards |
| 3 | Wortflüssigkeit | 20 min | 15 questions |
| 4 | Zahlenfolgen | 15 min | 10 questions |
| 5 | Ausweise Merken — Abfrage | 8 min | 25 questions |
| 6 | Implikationen erkennen | 10 min | 10 questions |

Each section draws its questions from a single **set** (e.g. set 0 = questions 1–15 for Figuren). When you correctly answer all questions in a set, the app advances to the next set. When all sets for a section are done, it wraps back to set 0.

Controls during the test:
- **A–E buttons** — select an answer
- **Überspringen** — skip the question (counts as wrong)
- **Zurück / Weiter** — navigate between questions
- **Timer ausblenden** — hide the countdown (timer keeps running)
- **Abbrechen** — quit the test without saving any progress

### Progress tracking

Your progress is saved **only when a section advances** (timer expires or you click "Nächster Abschnitt"). If you click "Abbrechen", nothing is saved.

Per section, the app stores:
- `currentSetIndex` — which set you're on
- `completed` — question IDs answered correctly (never shown again)
- `wrongIds` — question IDs answered incorrectly (shown again when the set recycles)

Correctly answered questions are skipped in future sessions. When all questions in the current set are completed correctly, the set index advances.

### Question types

| Section | Display |
|---------|---------|
| Figuren | Cropped figure image + A–E buttons |
| Ausweise Merken (memorize) | Allergy pass card image + fields (Name, DOB, blood type, allergies, etc.) — no answer buttons |
| Wortflüssigkeit | Letter sequence + A–E options |
| Zahlenfolgen | Number sequence + A–E options |
| Ausweise Merken (recall) | Question text (e.g. "What is the ID number of person X?") + A–E options |
| Implikationen | Premises + A–E logical conclusions |

### Anti-cheat hints

Sections where note-taking is forbidden in the real exam show an amber warning banner:
- **Figuren**: "✗ Notizen VERBOTEN: Keine Notizen, Markierungen oder Kreise im Heft erlaubt."
- **Ausweise Merken (memorize)**: "✗ Notizen VERBOTEN: In der Merkphase darfst du nichts aufschreiben."

## Project structure

```
medat-app/
├── app/                          # Electron + React desktop app
│   ├── package.json
│   ├── electron.vite.config.ts   # electron-vite build config (main/preload/renderer)
│   ├── electron-builder.yml      # electron-builder packaging config
│   ├── tsconfig.json             # Root tsconfig (references node + web)
│   ├── tsconfig.node.json        # Main + preload process types
│   ├── tsconfig.web.json         # Renderer process types
│   └── src/
│       ├── main/
│       │   └── index.ts          # Electron main process (BrowserWindow, IPC)
│       ├── preload/
│       │   ├── index.ts          # contextBridge (minimal, only ping stub)
│       │   └── index.d.ts        # Window.api type augmentation
│       └── renderer/
│           ├── index.html        # HTML entry point
│           └── src/
│               ├── main.tsx      # React root mount (StrictMode)
│               ├── App.tsx       # Screen router (login → home ↔ test/settings)
│               ├── index.css     # Tailwind v4 import
│               ├── vite-env.d.ts # Vite client type reference
│               ├── types.ts      # SectionKey, SectionConfig, Question,
│               │                 #   SectionProgress, UserProgress, Screen, SECTION_ORDER
│               ├── assets/
│               │   ├── questions.json  # 3,365 questions (bundled at build time)
│               │   ├── figuren/        # 255 cropped figure PNGs (001–255.png)
│               │   └── ausweise/       # 320 ID card PNGs (001–320.png)
│               ├── components/
│               │   ├── QuestionCard.tsx # Renders question content + A–E buttons
│               │   ├── Timer.tsx        # Progress bar + M:SS countdown
│               │   └── HintBanner.tsx   # "Notizen VERBOTEN" amber warning
│               ├── hooks/
│               │   └── useTimer.ts     # Countdown timer (start/pause/reset/expire)
│               ├── pages/
│               │   ├── Login.tsx       # Username input (remembers last user)
│               │   ├── Home.tsx        # Progress dashboard + start/settings buttons
│               │   ├── Test.tsx        # Full KFF test orchestrator
│               │   └── Settings.tsx    # Per-section set index override + reset
│               └── services/
│                   └── storage.ts      # localStorage wrapper + stats computation
│
└── data/                          # Python PDF extraction tooling
    ├── pyproject.toml             # uv-based project config (Python 3.13)
    ├── DATA_FORMAT.md             # Parser output schema & ID conventions
    ├── input/                     # Source PDFs by section
    │   ├── figuren/
    │   ├── implikationen/
    │   ├── wortfluessigkeit/
    │   ├── zahlenfolgen/
    │   └── ausweise/
    ├── output/                    # Parsed JSON + images by section
    │   ├── figuren/   (sets set_01–set_17, answers.json)
    │   ├── implikationen/ (sets set_01–set_07, answers.json)
    │   ├── wortfluessigkeit/ (sets set_001–set_110, answers.json)
    │   ├── zahlenfolgen/ (sets set_01–set_07, answers.json)
    │   └── ausweise/   (sets set_01–set_40, images/)
    └── src/
        └── medat_parser/
            ├── pdf_parser.py          # Unified entry point (dispatches to section parsers)
            ├── figuren_parser.py      # Figuren: PDF → JSON + cropped PNGs
            ├── implikationen_parser.py
            ├── wortfluessigkeit_parser.py
            ├── zahlenfolgen_parser.py
            ├── ausweise_parser.py     # Ausweise: PDF → card JSONs + recall questions
            ├── converter.py           # output/ → app's questions.json (flat by section)
            ├── merge.py               # Merges multiple PDF outputs into unified output/
            ├── models.py              # Pydantic data models
            └── utils.py               # Shared text extraction helpers
```

## Data pipeline

### Adding or updating questions

1. Place new PDFs in `data/input/<section>/`
2. Run the parser for that section:
   ```bash
   cd data
   uv run medat-parse --input input/ --output output/
   ```
   Or a single section:
   ```bash
   uv run python -m medat_parser.figuren_parser --input "input/figuren/new.pdf" --output output/figuren/
   ```
3. Run the converter to rebuild the app's question bundle:
   ```bash
   uv run medat-convert --input output --output ../app/src/renderer/src/assets/questions.json
   ```
4. If the parser produced images, copy them into the app assets:
   ```bash
   cp data/output/<section>/sets/set_*/*.png app/src/renderer/src/assets/<section>/
   ```
5. Rebuild the app (`npm run dev` or `npm run build`)

### Data format

See `data/DATA_FORMAT.md` for the complete parser output JSON schema and ID conventions.

The converter (`converter.py`) flattens the rich parser output into a simple `Record<section, Question[]>` JSON format:

```json
{
  "figuren": [
    {"section": "figuren", "id": 1, "answer": "C", "content": "[Bild: Figur 1]"}
  ],
  "ausweise_memorize": [
    {
      "section": "ausweise_memorize",
      "id": 1,
      "answer": "",
      "content": "Name: GILTONS\nGeburtstag: 22. März\n...",
      "image": "001.png"
    }
  ],
  "ausweise_recall": [
    {
      "section": "ausweise_recall",
      "id": 1,
      "answer": "E",
      "content": "WielautetdieAusweisnummer...\n\nA) 81942\nB) 23612\n..."
    }
  ]
}
```

### Current question counts (as of 2026-05-18)

| Section | Questions | Sets | Set Size |
|---------|-----------|------|----------|
| Figuren | 255 | 17 | 15 |
| Ausweise Merken (memorize) | 320 | 40 | 8 |
| Wortflüssigkeit | 1,650 | 110 | 15 |
| Zahlenfolgen | 70 | 7 | 10 |
| Ausweise Merken (recall) | 1,000 | 40 | 25 |
| Implikationen | 70 | 7 | 10 |
| **Total** | **3,365** | | |

## Tech stack

| Layer | Technology |
|-------|-----------|
| Desktop shell | Electron 33 |
| Build tooling | electron-vite 3, Vite 6 |
| UI | React 19, TypeScript 5.7 (strict) |
| Styling | Tailwind CSS v4 (Vite plugin, no config file) |
| Lint/format | oxlint, oxfmt |
| Data extraction | Python 3.13, uv, pdfplumber, PyMuPDF, Pillow, Pydantic |
| Lint/format (Python) | ruff, ty |
| Storage | localStorage (per-user progress), JSON files (questions) |
