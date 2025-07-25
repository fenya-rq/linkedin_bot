# Automatical Account Bot 🤖
### *keep your LinkedIn profile alive while you ship real features*

---

## ✨What the bot does
| Feature                        | Detail |
|--------------------------------|--------|
| **LinkedIn auto‑activity**     | Logs in with Playwright and makes **≥3 reposts per day** so your profile never looks idle. |
| **Headless & container‑ready** | Runs entirely inside Docker; schedule it in Kubernetes, cron, or a tiny VPS. |
| **AI-powered post analysis**   | Uses an **LLM agent via LangGraph** to analyze, filter, and summarize all scraped posts before reposting, ensuring only relevant and quality content is published. |
| **Config by environment**      | Credentials and options come from `.env` – no hard‑coding secrets. |
| **Poetry‑managed**             | Reproducible dependency graph, lock‑file, and handy `poetry run …` commands. |
| **Python 3.13.3**              | Built and tested on the latest CPython release. |
| **Async by design**            | Uses **async Playwright API** and `asyncio` to efficiently parallelize scraping, filtering, and reposting. |

---

## 📦 Technology stack
| Layer              | Tool / Version                                                   |
|--------------------|------------------------------------------------------------------|
| Language           | **Python=3.13.3**                                                |
| Dependency manager | **Poetry=1.8.2**                                                 |
| Browser automation | **Playwright=1.51.0 (async API)**                                |
| HTML parsing       | **beautifulsoup=44.13.3**                                        |
| Async runtime      | **asyncio=3.4.3**                                                |
| AI analysis        | **LangGraph + Gemini/ChatGPT agent integration**                 |
| Quality tools      | `ruff=0.11.5`, `pytest=8.3.5`, `mypy=1.15.0`, `pre‑commit=4.2.0` |
| Containerization   | **Docker / Docker Compose**                                      |

Full dependency declaration sits in **`pyproject.toml`** (excerpt).

## 🚀 Quick Start

### 1. Clone & configure

```bash
git clone https://github.com/fenya-rq/linkedin_bot
cd linkedin_bot
cp .env.example .env   # ← add your LinkedIn creds & settings here
```

### 2. Run service from same root directory
`docker compose up -d --build`

#### How it works

* After logging in the bot **scrapes ~60 fresh posts**, runs them through a **keyword filter** (only texts that match your configured words are kept), and queues the results for reposting.
* Runs them through an AI-powered LangGraph agent, which: Analyzes, filters, and summarizes each post for relevance and quality.
* Any interactions are dispatched at **random 30‑70 second intervals** to look human.
* **Adjustable volume** — simply put *15* instead of *3* on row **10** of docker‑compose.yml (`--posts_restrict 15`) to raise the limit to fifteen reposts per run.
* Entire process is asynchronous – powered by **asyncio** and **Playwright's async API** for responsive and efficient processing.

_Check logs can in the /var/log/accbot/._

Browsers – the Dockerfile bakes Chromium via
```playwright install --with-deps chromium```,
so no extra downloads happen at runtime.

## 🔮 Roadmap

| Status | Goal | Description |
|--------|------|-------------|
| 🟢 **Nextup** | **FastAPI WebUI & Robust Error‑Handling** | ① Harden the login flow with automatic CAPTCHA detection / solving hooks and graceful recovery from unexpected Playwright errors.<br>② Wrap the bot in a FastAPI service so you can create accounts, adjust keyword filters, and set daily repost limits from a browser. |
| 🟢 **Nextup** | **LLM‑powered repost logic** | Replace basic keyword matching with an embedded **LLM** that analyzes tone, content, and relevance of each post before deciding whether to repost. |
| 🟡 Planned | **Multi‑platform support** | Add adapters for Twitter, Instagram, and Facebook so one bot can keep *all* your socials warm. |
| 🟣 Ideas welcome | **Analytics dashboard** | Fancy charts, engagement alerts, and exportable reports. |

> **Contributions & ideas welcome — open an issue or PR!**

📄 License
MIT © 2025 Fenya‑rq
“Automation should work for you, not the other way around.” 🚀
