# Auth Server

Authentication server solution implementing OpenID Connect Provider using IdPyOIDC.

## Architecture

This project follows Domain-Driven Design (DDD), Command Query Responsibility Segregation (CQRS), and Dependency Injection/Inversion of Control (DI/IoC) principles.

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

## Project Structure

```
auth_server/
├── apps/
│   ├── webapi/          # Web API application (Python, FastAPI, IdPyOIDC)
│   └── webui/           # Web UI application (React Redux)
└── libs/
    ├── common/          # Shared utilities and interfaces
    ├── domain/          # Domain layer (business logic)
    ├── application/     # Application layer (orchestration)
    └── infrastructure/  # Infrastructure layer (external concerns)
```

## Setup

### WebAPI (Python)

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up configuration:
```bash
cp apps/webapi/config.yml.example apps/webapi/config.yml
# Edit apps/webapi/config.yml with your database settings
```

4. Run the application:

**Option 1: Using uvicorn from project root (Recommended)**
```bash
# From project root
uvicorn apps.webapi.main:app --reload
```

**Option 2: Using Python module**
```bash
# From project root
python -m apps.webapi
```

**Option 3: Using uvicorn from apps/webapi directory**
```bash
# From project root (PYTHONPATH needs to include project root)
PYTHONPATH=. cd apps/webapi && uvicorn main:app --reload
```

The app will be available at `http://localhost:8000` (or the port specified in config.yml).

### WebUI (React)

1. Install dependencies:
```bash
cd apps/webui
npm install
```

2. Run the application:
```bash
npm start
```

## Development

- Follow the architecture guidelines in [ARCHITECTURE.md](ARCHITECTURE.md)
- Use double underscore (`__`) for Python file naming: `user__entity.py`
- All async functions must have `_async` suffix
- Controllers must only work with DTOs
- Follow layer dependency rules strictly

## Technology Stack

- **Backend**: Python, FastAPI, IdPyOIDC
- **Frontend**: React, Redux
- **Database**: SQLAlchemy (ORM)
- **DI Container**: Custom DI container implementation
- **Type Checking**: mypy
