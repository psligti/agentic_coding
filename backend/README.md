# WebApp Backend

FastAPI backend application for the WebApp project.

## Features

- **FastAPI**: Modern, fast web framework with automatic API documentation
- **Async Support**: Asynchronous request handling for better performance
- **CORS**: Cross-Origin Resource Sharing configured for development
- **Type Hints**: Full type annotations with Pydantic models
- **Health Checks**: Built-in health check endpoints
- **API Documentation**: Automatic Swagger UI and ReDoc at `/docs` and `/redoc`

## Setup

### Prerequisites

- Python 3.11 or higher
- pip or uv package manager

### Installation

```bash
# Install dependencies
pip install -e .

# Or using uv (faster)
uv sync
```

### Development Setup

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Or using uv
uv sync --extra dev
```

## Running the Application

### Development Mode (with auto-reload)

```bash
# Using Python module
python -m main

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using the script

```bash
webapp-backend
```

## API Documentation

Once running, access the API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Available Endpoints

- `GET /` - Root endpoint with welcome message
- `GET /health` - Health check
- `GET /api/v1/info` - API information

## Project Structure

```
backend/
├── main.py           # FastAPI application entry point
├── pyproject.toml    # Python project configuration
├── README.md         # This file
└── api/              # API route modules
    ├── __init__.py
    └── routes.py     # Route definitions
```

## Configuration

The application uses environment variables for configuration:

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `CORS_ORIGINS`: Comma-separated list of allowed origins (default: *)

Example:

```bash
export HOST=0.0.0.0
export PORT=8000
export CORS_ORIGINS="http://localhost:3000,http://localhost:5173"

uvicorn main:app
```

## Testing

Run the test suite:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=.
```

## Code Quality

### Linting

```bash
ruff check .
```

### Type Checking

```bash
mypy .
```

## Adding Routes

1. Create route file in `api/` directory:
```python
# api/routes.py
from fastapi import APIRouter

router = APIRouter(prefix="/example", tags=["example"])

@router.get("/test")
async def test_endpoint():
    return {"message": "Hello from example"}
```

2. Register route in `main.py`:
```python
from api import routes

app.include_router(routes.router)
```

## License

MIT License - see LICENSE file for details
