# PAS — Personal Assistant System

> *"What was I thinking back then?"*

PAS is a personal assistant system built around one core idea: **state recall** — not just finding a piece of information, but recovering the mental context of a past thinking moment. What triggered it, where the thought was going, what was left unfinished.

It is not a note-taking app. It is not a knowledge management system. It is a conversation partner with memory — one that lives inside Obsidian, knows your past thinking, and can surface relevant old ideas while you're in the middle of a new conversation.

---

## The problem it solves

You've had a conversation with an AI, or written something down, or read a book and scribbled notes — and weeks later, you remember *that you thought something*, but not *what* you thought. The feeling is gone. The state is gone.

Standard note-taking tools solve "where did I put it." PAS solves "what was I actually thinking when I wrote it."

---

## How it works

Four components, each doing one thing:

| Component | Role |
|-----------|------|
| **Claude Code (CC)** | The only thinker. Handles ingestion, tagging, retrieval judgment, and deciding when to surface old ideas. |
| **Obsidian** | Storage. Your notes live here as plain Markdown files, untouched. |
| **Mem0** | Semantic search index. Stores vector embeddings of each note so CC can ask "what's related to this?" and get file paths back. |
| **Tags + links** | Structural index. Tags cluster similar notes; wikilinks are point-to-point connections you draw manually. |

When you open Obsidian and start a conversation via the Claudian plugin, CC is already in PAS mode. It reads a protocol file (`.pas/CLAUDE.md`) that tells it exactly how to behave — how to ingest content, how to write summaries, when to search, when to surface something.

### Two modes of retrieval

**Active**: You ask about an old idea. CC searches by tags, semantic similarity, and links, then returns the original text — not a summary of it.

**Passive**: You're talking about something new. CC notices a connection to something in your pool and taps you on the shoulder: *"You had a related thought before — want to see it?"*

### Two layers, two different rules

The system has two layers that are physically separate but searched together:

**The pool** holds your own thinking — conversations, notes, written pieces. The governing rule here is original preservation (see below). CC never rewrites anything in the pool.

**The knowledge layer** (`知识/`) holds fragments you've collected from the outside — sentences from articles, ideas from books, other people's arguments. This layer works differently: CC *can* synthesize and rewrite here, because the goal isn't to preserve your mental state but to build a living network of connected concepts. Fragments go into an inbox (`_inbox/`), get digested into concept pages (`concepts/`), and get linked to each other and to relevant pool notes. Islands form slowly — a fragment that sits isolated for months can suddenly connect to three others when a new one arrives.

The key distinction that keeps them separate: anything containing *your own* judgment, confusion, or reasoning belongs in the pool. Dry external knowledge goes to the knowledge layer. When in doubt, CC defaults to the pool — misclassifying your own thinking into the knowledge layer would cause it to be rewritten and lost.

Both layers are indexed in Mem0 (separate Qdrant collections) and searched in parallel when you ask a substantive question.

### The key design principle: original preservation

When content enters the pool, it is never rewritten or summarized in place. CC only *adds* to it — a YAML frontmatter block with tags, date, source type, and a one-line status summary ("what was left unresolved here"). The original words stay exactly as written.

This matters because state lives in unprocessed material. A summary of a thought is a description of the thought — reading it, you think you're back in the moment, but you're not.

---

## What you need

- **Windows** (the current setup is Windows-specific; paths and scripts assume Windows)
- **[Obsidian](https://obsidian.md/)** — free, local Markdown editor
- **[Claudian plugin](https://github.com/ClaudianAI/claudian)** for Obsidian — gives Claude Code a workspace inside Obsidian
- **[Claude Code](https://claude.ai/code)** — Anthropic's agentic coding tool, used here as the system's executor
- **Python 3.11** (x64) — for Mem0 and the embedding pipeline
- **A DeepSeek API key** — used by Mem0's LLM layer ([get one here](https://platform.deepseek.com/))
- **[AI Exporter](https://github.com/agoramachina/claude-exporter)** (optional) — Chrome extension to export conversations from Claude.ai, ChatGPT, Gemini into Markdown for ingestion

---

## Getting started

### 1. Clone this repository into your Obsidian vault

Your vault is the folder Obsidian uses as its library. Clone or download this repo into it:

```
your-vault/
└── pas-system/   ← clone here
```

### 2. Run the setup script

Open a terminal in the `pas-system/` folder and run:

```bat
setup.bat
```

This installs the Python dependencies from `requirements.txt` and checks whether `DEEPSEEK_API_KEY` is available in your environment. The key is stored in your system environment, never in any file. If Python is not on `PATH`, set `PAS_PYTHON` to your local `python.exe` path before running the script. In the examples below, replace `<python>` with `python`, `py -3.11`, or your own Python executable path.

### 3. Set up your ROOT.md

This repository includes a template `.pas/ROOT.md`. During setup and calibration, fill it with your own profile and tag vocabulary. Keep your completed `ROOT.md` local; it is personal context, not something to publish back to a public repo.

### 4. Verify Mem0

Run the test script to confirm the embedding pipeline and DeepSeek connection are working:

```
<python> test_mem0.py
```

If it completes without errors, Mem0 is ready.

### 5. Open Obsidian, start a conversation via Claudian

The root-level `CLAUDE.md` is the entry point. When Claudian starts a session, it injects this file as project instructions, which tells CC to immediately read `.pas/CLAUDE.md` and `.pas/ROOT.md` before doing anything else. CC is now in PAS mode.

To ingest a file: drop it in the vault, tell CC to process it. CC will convert it to Markdown if needed, add a frontmatter block, write a state summary, tag it, and sync it to Mem0. The original content is never touched.

---

## Repository structure

```
pas-system/
├── .pas/                   # System files (hidden in Obsidian)
│   ├── CLAUDE.md           # The full protocol — how CC behaves
│   ├── ROOT.md             # Template profile + tag vocabulary; fill locally
│   ├── mem0_config.py      # Mem0 singleton config
│   ├── hooks/              # Claude Code hooks (e.g. session transcript extraction)
│   ├── projects/           # Per-project context files, loaded on demand
│   └── docs/               # Design docs and build logs
├── pool/                   # Your notes live here (not in this repo)
├── conversations/          # Conversation notes (not in this repo)
├── 知识/                   # Knowledge layer: external fragments CC maintains
│   ├── _inbox/             # Drop fragments here, zero friction
│   ├── _待定/              # Fragments that didn't connect yet; review when you have time
│   ├── concepts/           # Concept pages CC builds and synthesizes
│   └── index.md            # Human-browsable index (CC uses Mem0, not this)
├── books/                  # Books, kept separate from your own thinking
├── CLAUDE.md               # Entry point loaded by Claudian on startup
├── setup.bat               # Environment setup script
└── test_mem0.py            # Mem0 connection test
```

The `.pas/` folder is a hidden folder — Obsidian doesn't show dot-prefixed folders by default, so your note view stays clean. You only see your own notes.

---

## Design notes

A few things that look unusual and why they are the way they are:

**No scoring formulas.** Many retrieval systems pre-compute relevance scores. PAS doesn't. Claude Code is a thinking model — it can read a summary and judge "does this connect to what we're talking about right now" better than any weighted formula. The tuning surface is the natural-language protocol file, not numerical thresholds.

**Summaries describe state, not content.** The `summary` field in each note's frontmatter answers: *"what was left unresolved here?"* — not "what does this note cover." A summary that says "discusses three dimensions of X" is useless for state recall. A summary that says "got stuck on the jump from A to B, gave an analogy but didn't push it through" is useful.

**Tags are CC's, links are yours.** CC writes tags from a controlled vocabulary. Wikilinks (`[[...]]`) are written only by you, manually, when you notice a specific connection worth preserving. CC never generates links. This separation keeps the graph meaningful — a link means *you noticed something*, not that an algorithm found surface similarity.

**The pool is a pile, not a hierarchy.** Notes go in chronologically without forced categorization. Cross-domain connections are the most valuable thing the system can surface — a rigid folder structure would cut them off.

---

## Current status

The pool layer (ingestion, active retrieval, passive triggering) is at Stage 2 and stable.

The knowledge layer is at Phase 1: fragments can be ingested, digested into concept pages, linked to each other and to pool notes, and searched in parallel with the pool. Systematic back-linking (Phase 3) and proactive prompting — CC flagging contradictions, gaps, or repeated unresolved themes (Phase 4) — are designed but not yet active.

The protocol and tooling are specific to one person's setup, but the design is general. If you want to adapt it, start with `.pas/CLAUDE.md` — that file is the whole system's brain. Everything CC does is controlled from there.

---

## License

MIT
