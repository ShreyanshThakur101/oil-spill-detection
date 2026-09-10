"""
Backend server entrypoint avoiding standalone executable wrappers.
Run with:
    python run.py
or
    uv run python run.py
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
