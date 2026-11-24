# AI Agents for Banking and Regulation

Hands-on materials for the AI sessions of the Data Analytics module of the [Master in Banking and Financial Regulation](https://en.unav.edu/web/masters-degree-in-banking-and-financial-regulation) (University of Navarra, Madrid campus), 2026-27.

- **Sessions:** 5 (Agent Architecture and Ecosystem Tools) and 6 (Guided Agent Construction), 4 h each.
- **Language:** English.
- **Audience:** business and regulation profiles with intermediate Python. No ML background needed.

## Programme

### Session 5 — Agent architecture and ecosystem tools

| Notebook | Content | Colab |
|---|---|---|
| [01 · Tool calling from scratch](notebooks/sesion5/01_tool_calling_from_scratch.ipynb) | The agent loop by hand with the provider SDK; tool design; human approval for actions | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/albertotb/curso-agentes-ia/blob/main/notebooks/sesion5/01_tool_calling_from_scratch.ipynb) |
| [02 · Agents with LangChain and LangGraph](notebooks/sesion5/02_agents_with_langchain.ipynb) | `create_agent`, provider switch, middleware (limits, human in the loop), memory, LangGraph workflows | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/albertotb/curso-agentes-ia/blob/main/notebooks/sesion5/02_agents_with_langchain.ipynb) |

### Session 6 — Guided agent construction

Group project: each group (~4 students) builds an agent for a banking or regulatory use case and presents it to a panel.

## Running the notebooks

- **Colab:** open a notebook with its badge above. Its first cell, `%pip install -q git+https://github.com/albertotb/curso-agentes-ia`, installs the dependencies and the course helpers (`from cai import utils`); the data is downloaded on first use.
- **Local:** see [Local setup](#local-setup).

## API keys

The notebooks work with **OpenAI** or **Google Gemini**. Set `PROVIDER` in the setup cell and provide the matching key:

- **Colab:** add a secret (key icon in the left bar) named `OPENAI_API_KEY` or `GEMINI_API_KEY` and give the notebook access to it.
- **Local:** copy `.env.template` to `.env` and fill in the key.

Never paste a key into a notebook cell or commit it.

### Gemini API key (free tier, personal account)

1. In an incognito window, sign in with your personal Google account and open <https://aistudio.google.com/apikey>.
2. Accept the terms if prompted.
3. Click **Create API key** and choose a new project or a personal one **without billing** (if the project has billing enabled, it is no longer free tier).
4. Check that the **Plan** column for the key says **Free**.
5. Save the key as described above (Colab secret or `.env`) and test it:
   ```bash
   source .env
   curl -s -H "x-goog-api-key: $GEMINI_API_KEY" https://generativelanguage.googleapis.com/v1beta/models | head -20
   ```

Outside the EEA, Switzerland and the UK, Google may use free-tier prompts and responses to improve its products; from those regions the [Gemini API terms](https://ai.google.dev/gemini-api/terms) apply the paid-tier data rules to free usage as well. Either way, do not send confidential data. The request limits for each model are in AI Studio → **Rate limits**.

## Data

All data is in [`data/raw/`](data/raw/). See [`data/README.md`](data/README.md).

- `bank.db`: SQLite database of a fictional bank (*Demo Bank*): customers, loans, transactions and quarterly capital position. Synthetic.
- `crr_articles.jsonl`: the Capital Requirements Regulation (EU) No 575/2013, consolidated text of 26 June 2026, one record per article.

## Local setup

```bash
# 1. Install uv (once): https://docs.astral.sh/uv/
# 2. Create the environment
uv sync
# 3. Start Jupyter
uv run jupyter lab
```

## Repository structure

```text
curso-agentes-ia/
├── README.md
├── CLAUDE.md                # Short notes for AI assistants
├── pyproject.toml           # Dependencies and config (uv + ruff)
├── .env.template            # API key names
├── data/
│   ├── README.md
│   └── raw/                 # bank.db, crr_articles.jsonl (versioned)
├── src/
│   └── cai/
│       └── utils.py         # Setup helpers: API keys, model clients, data loading
├── scripts/                 # Rebuild the data in data/raw/
└── notebooks/
    └── sesion5/
```
