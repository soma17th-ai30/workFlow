# syntax=docker/dockerfile:1

FROM node:22-alpine AS frontend-build

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend ./
RUN npm run build


FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./message_polishing/requirements.txt
RUN pip install --no-cache-dir -r ./message_polishing/requirements.txt

COPY __init__.py ./message_polishing/__init__.py
COPY API_SPEC.md README.md backend_trace.py context.py env.py graph.py llm.py prompts.py schemas.py settings.py web_server.py ./message_polishing/
COPY agents ./message_polishing/agents
COPY --from=frontend-build /app/frontend/dist ./message_polishing/frontend/dist

EXPOSE 8000

CMD ["python", "-m", "message_polishing.web_server", "--host", "0.0.0.0", "--port", "8000"]
