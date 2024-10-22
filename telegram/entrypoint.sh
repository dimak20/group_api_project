#!/bin/sh

# Run web server
uvicorn app.main:app --host 0.0.0.0 --port 8082 --reload --reload-dir /usr/src/fastapi/app
