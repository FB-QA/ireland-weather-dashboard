# Tests for Ireland Weather Dashboard

## Setup

Activate the project virtualenv and install test dependencies:

```bash
source venv/bin/activate
pip install pytest pytest-asyncio httpx respx
```

## Running Tests

From the project root:

```bash
# Run all tests with verbose output
pytest tests/ -v

# Run only unit tests
pytest tests/unit/ -v

# Run only API tests
pytest tests/api/ -v

# Run a specific test file
pytest tests/api/test_weather.py -v
```

## Test Structure

```
tests/
  conftest.py                  # Shared fixtures (async FastAPI test client)
  unit/
    test_main.py               # COUNTIES data integrity, _validate_coordinates
  api/
    test_counties.py           # GET /api/counties endpoint
    test_weather.py            # GET /api/weather endpoint (mocked upstream)
```

## Notes

- API tests use `httpx.AsyncClient` with `ASGITransport` to call the FastAPI app directly (no running server required).
- External HTTP calls to Open-Meteo are mocked with `respx` so tests run offline and fast.
- `pytest-asyncio` is configured in `pytest.ini` with `asyncio_mode = auto`.
