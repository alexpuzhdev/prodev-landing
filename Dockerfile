FROM node:22-alpine AS frontend
WORKDIR /build
COPY shared/ shared/
COPY frontend/package.json frontend/package-lock.json frontend/
RUN cd frontend && npm ci
COPY frontend/ frontend/
RUN cd frontend && npm run build

FROM python:3.12-slim
WORKDIR /srv
COPY backend/pyproject.toml backend/
COPY backend/app backend/app
COPY shared/ shared/
RUN pip install --no-cache-dir ./backend
COPY --from=frontend /build/frontend/dist frontend/dist
ENV DB_PATH=/srv/data/content.db \
    SEED_PATH=/srv/shared/seed_content.json \
    STATIC_DIR=/srv/frontend/dist
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "backend"]
