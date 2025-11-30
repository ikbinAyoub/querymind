# SQL-RAG System - Copilot Instructions

## Project Overview
A universal SQL-RAG interface that allows users to connect to PostgreSQL databases and ask questions in natural language, which are automatically translated into SQL queries.

## Tech Stack
- **Backend**: Python 3.11+, FastAPI, async SQLAlchemy 2.0
- **Database**: PostgreSQL (via asyncpg)
- **LLM**: OpenAI GPT / Azure OpenAI
- **Cache**: Redis
- **Deployment**: Docker, Docker Compose

## Project Structure
```
sql-rag-system/
├── backend/
│   └── app/
│       ├── api/routes/          # FastAPI endpoints
│       ├── core/                # Security, exceptions, config
│       ├── db/adapters/         # Database adapters (PostgreSQL)
│       ├── llm/                 # LLM integration, prompt building
│       ├── executor/            # Query execution
│       ├── postprocessor/       # Result formatting
│       ├── cache/               # Redis caching
│       └── models/              # Pydantic models
├── docker/                      # Docker configuration
└── tests/                       # Unit and integration tests
```

## Coding Guidelines
- Use async/await for all I/O operations
- Follow PEP 8 style guidelines
- Use type hints consistently
- Implement comprehensive error handling
- Write docstrings for all public functions
- Keep functions focused and modular

## Security Rules
- Never execute DROP, DELETE, TRUNCATE, ALTER, CREATE, INSERT, UPDATE queries
- Validate all SQL before execution
- Use parameterized queries
- Sanitize user inputs
- Implement connection timeouts

## API Design
- RESTful endpoints
- Consistent error responses
- OpenAPI documentation
- Request validation with Pydantic
