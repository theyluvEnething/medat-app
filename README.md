# MedAT KFF Trainer

Offline study app for the Kognitive Fähigkeiten und Fertigkeiten (KFF) section of the Austrian MedAT medical school entrance exam.

Runs full timed KFF test simulations in an Electron desktop app — same section order, same time limits, same question counts as the real exam.

## Setup

### App

```bash
cd app
npm install
npm run dev
```

### Data parser (optional — only if extracting questions from new PDFs)

```bash
cd data
uv sync
```

## Test sections

1. **Figuren zusammensetzen** — 20 min, 15 questions
2. **Ausweise Merken (memorize)** — 8 min, 25 items
3. **Zahlenfolgen** — 15 min, 10 questions
4. **Wortflüssigkeit** — 20 min, 15 questions
5. **Ausweise Merken (recall)** — 25 questions
6. **Implikationen erkennen** — 10 min, 10 questions

## Project structure

```
data/    Python tooling for extracting questions from PDFs into JSON
app/     Electron + Vite + React + TypeScript + Tailwind desktop app
```
