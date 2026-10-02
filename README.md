FastAPI Project

A high-performance REST API built with FastAPI (https://fastapi.tiangolo.com/) and managed using uv (https://github.com/astral-sh/uv) for lightning-fast Python dependency management.

--------------------------------------------------------------------------------
FEATURES

* FastAPI: Modern, fast (high-performance) web framework for building APIs.
* uv Package Manager: Extremely fast Python package installer and resolver.
* Automatic Interactive Docs: Swagger UI and ReDoc provided out-of-the-box.
* Pydantic: Data validation and settings management.

--------------------------------------------------------------------------------
PREREQUISITES

* Python 3.8+
* uv installed on your system. 
  (Install via `curl -LsSf https://astral.sh/uv/install.sh | sh` on macOS/Linux 
  or `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"` on Windows)

--------------------------------------------------------------------------------
INSTALLATION & SETUP

1. Clone the repository:
   git clone https://github.com/RohitSingh-04/AML_OSDD_Helper.git
   cd AML_OSDD_Helper
2. Create a virtual environment using uv:
   uv venv

3. Activate the virtual environment:
   * Linux/macOS:
     source .venv/bin/activate
   * Windows:
     .venv\Scripts\activate

4. Install dependencies:
   uv pip install -r requirements.txt
   
   (Note: If you add new packages during development, use `uv pip install <package_name>` 
   and update your requirements file with `uv pip freeze > requirements.txt`)

--------------------------------------------------------------------------------
ENVIRONMENT VARIABLES

Copy the sample environment file and configure your local variables:
cp .env.example .env

--------------------------------------------------------------------------------
RUNNING THE APPLICATION

Start the FastAPI server with live reloading enabled for development:
uvicorn app.main:app --reload

The API will be available at http://127.0.0.1:8000

--------------------------------------------------------------------------------
API DOCUMENTATION

Once the server is running, you can explore the API endpoints via:
* Swagger UI: http://127.0.0.1:8000/docs
* ReDoc: http://127.0.0.1:8000/redoc

--------------------------------------------------------------------------------
PROJECT STRUCTURE

├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application instance and entry point
│   ├── api/              # API routers and endpoints
│   ├── core/             # Application configuration and security
│   ├── models/           # Database models
│   ├── schemas/          # Pydantic validation schemas
│   └── services/         # Business logic
├── tests/                # Pytest test suite
├── .env.example          # Template for environment variables
├── requirements.txt      # Project dependencies
└── README.txt

--------------------------------------------------------------------------------
TESTING

Run the test suite using pytest:
uv pip install pytest httpx
pytest