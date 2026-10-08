# AML OSDD Analyzer

An AI-powered Open Source Due Diligence (OSDD) analyzer built with **FastAPI, SerpAPI, Ollama, and LangChain**.

The application searches public sources, extracts information from HTML/PDF/YouTube sources, concurrently distills findings into structured observations, and synthesizes a comprehensive final OSDD risk assessment. It now includes a web dashboard for easier interaction.

## Demo

[![AML OSDD Analyzer Demo](https://img.youtube.com/vi/utdR_B4uJk0/0.jpg)](https://youtu.be/utdR_B4uJk0)

*Click the image above or [here](https://youtu.be/utdR_B4uJk0) to watch the demo video on YouTube.*

## Architecture

The system utilizes a Map-Reduce LLM pattern to handle large volumes of context efficiently, governed by local concurrency limits (Semaphores) to prevent Ollama from overloading.

```text
                         ┌─────────────────────┐
                         │       FastAPI       │
                         │ GET / (Dashboard)   │
                         │ POST /api/analyze   │
                         └──────────┬──────────┘
                                    │
                              ┌─────┴─────┐
                              │  SerpAPI  │
                              └─────┬─────┘
                                    │
                 ┌──────────────────┼──────────────────┐
                 ▼                  ▼                  ▼
           Entity Search      Address Search      Negative News
                 │                  │                  │
                 └──────────────────┼──────────────────┘
                                    ▼
                      Source Extraction (Trafilatura,
                      PyMuPDF, YouTube Transcripts)
                                    │
                 ┌──────────────────┼──────────────────┐
                 ▼                  ▼                  ▼
              Source 1           Source 2           Source N
            Distillation       Distillation       Distillation
            (Concurrent)       (Concurrent)       (Concurrent)
                 │                  │                  │
                 └──────────────────┼──────────────────┘
                                    ▼
                             Evidence Dossier
                                    │
                                    ▼
                           Final LLM Synthesis
                          (LangChain + Pydantic)
                                    │
                                    ▼
                             FinalOSDDResult
```

### Project Structure

```text
aml_osdd_helper/
│
├── src/
│   └── aml_osdd_helper/
│       ├── __init__.py
│       ├── main.py
│       ├── pipeline.py       # Orchestrates Map-Reduce & concurrency
│       ├── models.py         # Pydantic schemas for structured extraction
│       ├── prompts.py        # Distillation and synthesis prompts
│       ├── scraper.py        # SerpAPI and text extraction
│       ├── llm.py            # LangChain integrations & Semaphore limits
│       ├── logger.py         # Application logging
│       ├── settings.py       # Configuration
│       ├── static/           # CSS/JS for the dashboard
│       └── templates/        # Jinja2 HTML templates for the UI
│
├── logs/
│   └── aml_osdd_logs.log
├── requirements.txt
├── pyproject.toml
├── uv.lock
├── .python-version
├── .env
├── .gitignore
└── LICENSE
```

## Features

- **Web Dashboard:** Interactive frontend built with Jinja2 templates and FastAPI.
- **Google Search Integration:** Powered by SerpAPI (Entity, Address, and Negative News buckets).
- **Multi-Format Extraction:** Handles standard HTML (Trafilatura), PDFs (PyMuPDF), and YouTube transcripts.
- **Concurrent Source Distillation (Map-Reduce):** Processes multiple extracted URLs in parallel using an asyncio semaphore to prevent local LLM timeout/OOM.
- **Structured AI Outputs:** Leverages `langchain_core` and `PydanticOutputParser` to ensure consistent JSON outputs (`FinalOSDDResult`, `RiskFactor`, `SanctionsResult`).
- **Deep Risk Analysis:** Automatically identifies PEP associations, sanctions flags, adverse media, related entities, and generates a quantitative risk score (0-100).
- **Local LLM Inference:** Built for privacy using local models via Ollama.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- Ollama
- A compatible Ollama model
- SerpAPI account/API key

## Installation

Clone the repository:

```bash
git clone "https://github.com/RohitSingh-04/AML_OSDD_Helper"
cd AML_OSDD_Helper
```

Create the virtual environment:

```bash
uv venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

Install the dependencies:

```bash
uv add -r requirements.txt
```

Start Ollama:

```bash
ollama serve
```

Pull your desired model if it is not already installed (e.g., dolphin3):

```bash
ollama pull dolphin3:latest
```

## Environment Variables

Create a `.env` file in the project root. It must include the following variables:

```env
SERPAPI_API_KEY="your key here"
OLLAMA_MODEL="choosen model"
OLLAMA_CONCURRENCY_LIMIT=int of concurrent request of ollama
```

### Variable Descriptions

| Variable | Description |
|---|---|
| `SERPAPI_API_KEY` | API key used for Google and YouTube searches |
| `OLLAMA_MODEL` | Ollama model used by the application (e.g., `dolphin3:latest`) |
| `OLLAMA_CONCURRENCY_LIMIT` | Controls how many parallel LLM distillation tasks run at once (e.g., `3`) |

Check installed Ollama models with:

```bash
ollama list
```

## Running the Application

Start the FastAPI development server using `uv`:

```bash
uv run fastapi dev src/aml_osdd_helper/main.py
```

Alternatively, you can run it with Uvicorn directly:

```bash
uv run uvicorn src.aml_osdd_helper.main:app --reload
```

- **Dashboard:** `http://127.0.0.1:8000/`
- **API Documentation:** `http://127.0.0.1:8000/docs`

## API Usage

### `GET /`

Serves the web dashboard (HTML UI) where you can input entity details and view the generated report visually.

### `POST /api/analyze`

**Request (`AnalyzeRequest`):**

```json
{
    "entity_name": "Crown Resorts",
    "address": ""
}
```

The API performs:
1. Search collection via SerpAPI.
2. Concurrent context extraction for all identified URLs.
3. Parallel distillation of each source (`SectionDistillation`) to isolate AML findings.
4. Aggregation of a master evidence dossier.
5. Final structured LLM synthesis (`FinalOSDDResult`).

**Response Schema (`FinalOSDDResult`):**
Returns a strictly typed JSON structure containing:
- Basic entity profiling (Type, Industry, Jurisdiction).
- Discovered Addresses & Related Entities.
- `RiskFactor` array (Category, Description, Severity).
- `SanctionsResult` (Flags, Details, Sources).
- PEP Association and Negative News tracking.
- Overall `risk_score` (0-100) and `risk_level` (Very Low to Critical).

Example using `curl`:

```bash
curl -X POST "http://127.0.0.1:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"entity_name\":\"Crown Resorts\",\"address\":\"\"}"
```

## Logging

Application logs are displayed in the console and written to:

```text
logs/aml_osdd_logs.log
```

The logging system tracks the entire map-reduce pipeline:
- Search initiation and source counts.
- Concurrent distillation progress (and extraction fallbacks).
- Pydantic parser retries/errors.
- Final synthesis completion and assigned risk scores.

## Disclaimer

This project is intended as an **OSINT/OSDD research and assistance tool**. Results generated from public sources and LLMs should be reviewed and verified by an appropriate human before being used for compliance, legal, or business decisions. The automated scoring is suggestive based on publicly scraped context and does not replace official KYC/AML procedures.