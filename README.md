# AML OSDD Analyzer

An AI-powered Open Source Due Diligence (OSDD) analyzer built with **FastAPI, SerpAPI, Ollama, and LangChain**.

The application searches public sources, extracts information from HTML/PDF/YouTube sources, summarizes large search results into LLM-sized batches, and generates a structured OSDD assessment.

## Architecture

```text
                         ┌─────────────────────┐
                         │       FastAPI       │
                         │   POST /api/analyze │
                         └──────────┬──────────┘
                                    │
                                    ▼
                              ┌───────────┐
                              │  SerpAPI  │
                              └─────┬─────┘
                                    │
                 ┌──────────────────┼──────────────────┐
                 ▼                  ▼                  ▼
           Entity Search      Address Search      Negative News
                 │                  │                  │
                 └──────────────────┼──────────────────┘
                                    ▼
                           Source Extraction
                                    │
                  ┌─────────────────┼─────────────────┐
                  ▼                 ▼                 ▼
                HTML               PDF             YouTube
             Trafilatura         PyMuPDF          Transcript
                  │                 │                 │
                  └─────────────────┼─────────────────┘
                                    ▼
                            Context Batching
                                    │
                                    ▼
                         Source Summarization LLM
                                    │
                  ┌─────────────────┼─────────────────┐
                  ▼                 ▼                 ▼
             Entity Summary    Address Summary    News Summary
                  │                 │                 │
                  ▼                 ▼                 ▼
                LLM 1             LLM 2             LLM 3
                  │                 │                 │
                  └─────────────────┼─────────────────┘
                                    ▼
                                  LLM 4
                           Final Risk Assessment
                                    │
                                    ▼
                            FinalOSDDResult
```

### Project Structure

```text
aml-osdd-analyzer/
│
├── main.py
├── models.py
├── prompts.py
├── scraper.py
├── summarizer.py
│
├── logs/
│   └── aml_osdd_logs.log
│
├── requirements.txt
├── pyproject.toml
├── uv.lock
├── .python-version
├── .env
├── .gitignore
└── LICENSE
```

## Features

- Google search through SerpAPI
- Entity, address, and negative-news search buckets
- HTML extraction using Trafilatura
- PDF extraction using PyMuPDF
- YouTube transcript extraction
- Context-aware source batching
- LLM-based source summarization
- Structured LLM outputs using Pydantic
- Entity and address analysis
- Adverse-media analysis
- Final OSDD risk assessment
- Console and file logging
- Local LLM inference through Ollama

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

Pull your desired model if it is not already installed:

```bash
ollama pull dolphin3:latest
```

## Environment Variables

Create a `.env` file in the project root:

```env
SERPAPI_API_KEY=your_serpapi_api_key
OLLAMA_MODEL=dolphin3:latest
```

### Required Variables

| Variable | Description |
|---|---|
| `SERPAPI_API_KEY` | API key used for Google and YouTube searches |
| `OLLAMA_MODEL` | Ollama model used by the application |

`OLLAMA_MODEL` can be changed to any compatible model available locally.

For example:

```env
OLLAMA_MODEL=dolphin3:latest
```

Check installed Ollama models with:

```bash
ollama list
```

## Running the Application

Start the FastAPI server:

```bash
uv run uvicorn main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

## API Usage

### `POST /api/analyze`

Request:

```json
{
    "entity_name": "Crown Resorts",
    "address": ""
}
```

The API performs:

1. Entity search
2. Address search
3. Negative-news search
4. Source extraction
5. Context-aware summarization
6. Entity analysis
7. Address analysis
8. Negative-news analysis
9. Final OSDD assessment

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

The logging system records:

- Analysis start/completion
- Search and summarization stages
- LLM execution stages
- Errors and full tracebacks
- Debug-level model results

Example:

```text
2026-10-02 22:40:12 - aml_osdd_helper - INFO -
[OSDD ANALYSIS START] Entity: Crown Resorts | Address:

2026-10-02 22:40:15 - aml_osdd_helper - INFO -
Summarizing entity sources...

2026-10-02 22:40:42 - aml_osdd_helper - INFO -
[LLM 1]: Executing entity analysis

2026-10-02 22:41:20 - aml_osdd_helper - INFO -
[OSDD ANALYSIS COMPLETE] Successfully analyzed: Crown Resorts
```

## Disclaimer

This project is intended as an **OSINT/OSDD research and assistance tool**. Results generated from public sources and LLMs should be reviewed and verified by an appropriate human before being used for compliance, legal, or business decisions.