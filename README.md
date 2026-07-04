# StreamLine - Autonomous Decision Intelligence Platform

StreamLine is a production-ready AI SaaS platform designed to offer businesses autonomous decision intelligence capabilities. The repository integrates a Next.js frontend alongside a Clean Architecture FastAPI backend.

## Tech Stack
* **Frontend**: Next.js, React, Tailwind CSS, TypeScript
* **Backend**: Python 3.12, FastAPI, Pydantic v2, Google Cloud Storage, BigQuery, Gemini API, RAPIDS cuDF, cuML, Firebase Authentication (ready)
* **DevOps**: Docker, Docker Compose, Makefile

---

## Backend Directory Structure
The backend codebase resides side-by-side with the frontend within the root and the `app/` folder, organized under clear architectural bounds:

```
app/
├── main.py                 # FastAPI Application entry point and router registration
├── api/                    # API Routers (organized by version v1)
│   └── v1/                 # Endpoints injecting service layers
├── core/                   # Infrastructure configuration, structured logging, middleware, security
├── database/               # Database client adapters (BigQuery, Google Cloud Storage)
├── models/                 # Domain objects and core business entities
├── schemas/                # Pydantic v2 request & response validation schemas
├── services/               # Application service layers executing domain logic
└── repositories/           # Data access repository layers following the Repository Pattern
```

---

## Setup & Running the Backend

### Prerequisites
1. Python 3.12+
2. Docker & Docker Compose (optional)

### Local Development
1. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```
2. Install Python dependencies:
   ```bash
   make install
   ```
3. Copy environment variables file and configure it:
   ```bash
   cp .env.example .env
   ```
4. Run the FastAPI development server:
   ```bash
   make run
   ```
   The interactive API documentation will be available at `http://localhost:8000/docs`.

### Running with Docker Compose
To run the application inside a Docker container:
```bash
make docker-up
```
To tear down the containers:
```bash
make docker-down
```

### Formatting, Linting, & Testing
We use `ruff`, `black`, and `mypy` to maintain high code quality:
* **Format code**: `make format`
* **Lint code**: `make lint`
* **Run tests**: `make test`

---

## Architectural Principles
1. **SOLID Principles**: Each module and class has a single responsibility. We use interface definitions and abstract classes for decoupling code.
2. **Repository Pattern**: Data persistence details (BigQuery, GCS, etc.) are abstracted away behind repository interfaces, making it trivial to swap storage engines.
3. **Service Pattern**: Business logic is encapsulated in isolated services which are injected into API handlers.
4. **Dependency Injection**: FastAPI's native dependency injection (`Depends`) is used to resolve and mock repositories and services during runtime and testing.
