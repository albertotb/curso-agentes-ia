"""Setup helpers shared by the course notebooks: API keys, model clients and data."""

import contextlib
import json
import os
import sqlite3
import threading
import urllib.request
from pathlib import Path

DEFAULT_MODELS = {"openai": "gpt-5.4-mini", "gemini": "gemini-3.5-flash-lite"}
EMBEDDING_MODELS = {"openai": "text-embedding-3-small", "gemini": "gemini-embedding-001"}
KEY_NAMES = {"openai": "OPENAI_API_KEY", "gemini": "GEMINI_API_KEY"}
GEMINI_OPENAI_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
DATA_URL = "https://raw.githubusercontent.com/albertotb/curso-agentes-ia/main/data/raw"
# Present only when the repo is cloned (editable install); otherwise files are downloaded.
REPO_DATA = Path(__file__).resolve().parents[2] / "data" / "raw"


def get_api_key(name: str) -> str:
    """Colab secret > environment variable or .env file > ask (hidden input)."""
    # Fails outside Colab, or when the secret is missing / not shared with the notebook.
    with contextlib.suppress(Exception):
        from google.colab import userdata

        return userdata.get(name)
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass
    if os.environ.get(name):
        return os.environ[name]
    from getpass import getpass

    return getpass(f"{name}: ")


def get_client(provider: str):
    """OpenAI SDK client for `provider`; Gemini is reached through its OpenAI-compatible endpoint."""
    from openai import OpenAI

    base_url = GEMINI_OPENAI_URL if provider == "gemini" else None
    # max_retries: back off and retry on 429 (rate limit) and 5xx (overloaded) errors.
    return OpenAI(api_key=get_api_key(KEY_NAMES[provider]), base_url=base_url, max_retries=5)


def get_chat_model(provider: str, model: str | None = None):
    """LangChain chat model for `provider`.

    Gemini uses the native integration: Gemini 3 needs the thought signature of each tool call sent
    back, and the OpenAI-compatible client drops it (HTTP 400).
    """
    from langchain.chat_models import init_chat_model

    lc_provider = {"openai": "openai", "gemini": "google_genai"}[provider]
    model = model or DEFAULT_MODELS[provider]
    return init_chat_model(
        f"{lc_provider}:{model}", api_key=get_api_key(KEY_NAMES[provider]), max_retries=5
    )


def data_path(filename: str) -> Path:
    """Path to a file of data/raw/, downloading it to the current directory if the repo is not cloned."""
    if (REPO_DATA / filename).exists():
        return REPO_DATA / filename
    local = Path(filename)
    if not local.exists():
        urllib.request.urlretrieve(f"{DATA_URL}/{filename}", local)
    return local


class BankDB:
    """`db.execute(...)` on the synthetic Demo Bank database; rows behave like dicts (`dict(row)`).

    One SQLite connection per thread: agents run parallel tool calls in threads, and a shared
    connection fails with "InterfaceError: bad parameter or other API misuse".
    """

    def __init__(self, path: Path):
        self.path = path
        self.local = threading.local()

    def execute(self, sql: str, params=()) -> sqlite3.Cursor:
        if not hasattr(self.local, "conn"):
            self.local.conn = sqlite3.connect(self.path)
            self.local.conn.row_factory = sqlite3.Row
        return self.local.conn.execute(sql, params)


def load_bank_db() -> BankDB:
    """Connection to the synthetic Demo Bank database; rows behave like dicts (`dict(row)`)."""
    return BankDB(data_path("bank.db"))


def load_crr_articles() -> list[dict]:
    """The CRR, one dict per article (see data/README.md for the fields)."""
    with open(data_path("crr_articles.jsonl"), encoding="utf-8") as f:
        return [json.loads(line) for line in f]
