# MedAT KFF Trainer

Realistic KFF (Kognitive Fähigkeiten und Fertigkeiten) test simulator for the Austrian MedAT entrance exam. Runs timed full-length simulations matching the real exam — same section order, same time limits, same question counts.

**Try it online:** https://theyluvenething.github.io/medat-app/

Built with **Electron + Vite + React 19 + TypeScript + Tailwind CSS v4**. Available as both a desktop app and a website.

## Quick start

### Web (browser)

```bash
cd web
npm install
npm run dev          # Vite dev server at localhost:5173
```

### Desktop (Electron)

```bash
cd app
npm install
npm run dev          # Electron window at 1280×720
```

Requires **Node ≥ 22**.

## Screens

| Route | Screen | Purpose |
|-------|--------|---------|
| `/login` | Login | Username entry with persistence |
| `/home` | Home | Progress dashboard, streak, mastery levels |
| `/setup` | Setup | Full KFF simulation or single category practice |
| `/session/:type` | Session | Active quiz with Busuu-style QuizCard |
| `/results` | Results | Post-session analytics and wrong-answer review |
| `/settings` | Settings | Per-section set control + progress reset |
| `/leaderboard` | Leaderboard | Global ranking powered by Supabase |

## Test flow

The app runs 6 sequential sections matching the real MedAT KFF:

| # | Section | Time | Per Set |
|---|---------|------|---------|
| 1 | Figuren zusammensetzen | 20 min | 15 questions |
| 2 | Ausweise Merken — Einprägen | 8 min | 8 cards |
| 3 | Wortflüssigkeit | 20 min | 15 questions |
| 4 | Zahlenfolgen | 15 min | 10 questions |
| 5 | Ausweise Merken — Abfrage | 8 min | 25 questions |
| 6 | Implikationen erkennen | 10 min | 10 questions |

Each section draws questions from fixed-size **sets**. When all questions in a set are answered correctly, the set advances. Wrong answers reappear when the set recycles.

### Setup modes

- **Full KFF Simulation**: All 6 sections sequentially with strict timing
- **Single Category**: Pick one section (e.g. only "Zahlenfolgen") for focused practice

## Progress & gamification

**localStorage persistence** — progress saved automatically after each section. Zustand store tracks:

- **Per-section progress**: current set index, completed question IDs, wrong-question IDs
- **Daily streak**: consecutive active days, displayed with fire emoji
- **Mastery levels**: 0–100% accuracy per category, shown as Bronze/Silver/Gold
- **Wrong-question tracking**: counts per question for spaced repetition review

Progress is only saved when a section advances (timer expiry or manual "Fertig"). Clicking "Abbrechen" exits without saving.

## Leaderboard

Global ranking powered by **Supabase** (REST API, public anon key). The leaderboard shows:

- Ranked users sorted by total score (highest first)
- Questions solved and correct percentage
- Auto-refreshes every 30 seconds
- Top-3 podium display

Data is submitted automatically when a user completes a session.

## Question types

| Section | Display |
|---------|---------|
| Figuren | Cropped figure image + A–E buttons |
| Ausweise Merken (memorize) | ID card image + fields (Name, DOB, blood type, etc.) — no answer buttons |
| Wortflüssigkeit | Letter sequence + A–E options |
| Zahlenfolgen | Number sequence + A–E options |
| Ausweise Merken (recall) | Question text + A–E options |
| Implikationen | Premises + A–E logical conclusions |

## Project structure

```
medat-app/
├── app/                          # Electron + React desktop app
│   ├── package.json
│   ├── electron.vite.config.ts
│   ├── electron-builder.yml
│   └── src/
│       ├── main/index.ts         # Electron main process
│       ├── preload/              # contextBridge (minimal)
│       └── renderer/src/
│           ├── main.tsx          # React root + HashRouter
│           ├── App.tsx           # Route definitions
│           ├── types.ts          # SectionKey, Question, SessionRecord, etc.
│           ├── index.css         # Tailwind v4 + custom animations
│           ├── assets/           # questions.json + figuren/ausweise/solutions PNGs
│           ├── components/
│           │   ├── QuizCard.tsx       # Busuu-style question card
│           │   ├── ProgressTracker.tsx # Green/red/gray square row
│           │   ├── Timer.tsx          # Progress bar + M:SS countdown
│           │   └── HintBanner.tsx     # "Notizen VERBOTEN" warning
│           ├── hooks/
│           │   └── useTimer.ts        # Countdown timer hook
│           ├── pages/
│           │   ├── Login.tsx, Home.tsx, Setup.tsx
│           │   ├── Session.tsx, Results.tsx
│           │   ├── Settings.tsx, Leaderboard.tsx
│           ├── services/
│           │   ├── storage.ts         # Legacy localStorage helpers
│           │   └── supabase.ts        # Supabase REST client
│           └── store/
│               └── useAppStore.ts     # Zustand store with persist
│
├── web/                          # Standalone web build
│   ├── package.json
│   ├── vite.config.ts            # @app alias + dedupe config
│   ├── tsconfig.json
│   ├── index.html
│   └── src/
│       ├── main.tsx              # Entry (imports App from @app)
│       ├── index.css             # @source for app tree scanning
│       ├── env.d.ts              # Web type declarations
│       └── environment.ts        # Electron/browser platform abstraction
│
└── data/                         # Python PDF extraction tooling
    ├── pyproject.toml
    ├── DATA_FORMAT.md
    ├── input/                    # Source PDFs by section
    ├── output/                   # Flat text files + images
    └── src/medat_parser/         # Section parsers + converter
```

## Tech stack

| Layer | Technology |
|-------|-----------|
| Desktop shell | Electron 33 |
| Web deployment | Vite 6 → GitHub Pages |
| UI | React 19, TypeScript 5.7 (strict) |
| Routing | React Router v7 (HashRouter) |
| State | Zustand v5 (persist middleware) |
| Styling | Tailwind CSS v4 (Vite plugin) |
| Leaderboard | Supabase (PostgREST API) |
| Data extraction | Python 3.13, uv, pdfplumber, PyMuPDF, Pillow |

## Data pipeline

### Adding or updating questions

1. Place PDFs in `data/input/<section>/`
2. Parse: `cd data && uv run medat-parse --input input/ --output output/`
3. Convert: `uv run medat-convert --input output --output ../app/src/renderer/src/assets/questions.json`
4. Copy images (strip `_question` suffix for app compat):
   ```bash
   for f in data/output/figuren/*_question.png; do
       base=$(basename "$f" _question.png)
       cp "$f" "app/src/renderer/src/assets/figuren/${base}.png"
   done
   ```
5. Rebuild: `cd app && npm run dev`

### Current question counts

| Section | Questions | Sets | Set Size |
|---------|-----------|------|----------|
| Figuren | 255 | 17 | 15 |
| Ausweise Merken (memorize) | 320 | 40 | 8 |
| Wortflüssigkeit | 1,650 | 110 | 15 |
| Zahlenfolgen | 70 | 7 | 10 |
| Ausweise Merken (recall) | 1,000 | 40 | 25 |
| Implikationen | 70 | 7 | 10 |
| **Total** | **3,365** | | |

## Web deployment

```bash
cd web
npm run build          # → dist/
# Deploy dist/ contents to gh-pages branch:
# git subtree push or manual copy to orphan gh-pages branch
```

Served at `https://theyluvenething.github.io/medat-app/` via GitHub Pages with base path `/medat-app/`.
