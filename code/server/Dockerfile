# Build frontend
FROM node:22 AS frontend-builder
WORKDIR /app/frontend
COPY code/frontend/package*.json ./
RUN npm ci
COPY code/frontend ./
RUN npm run build

# Build backend
FROM python:3.11
WORKDIR /app
COPY code/server/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY code/server/server.py ./server.py
COPY --from=frontend-builder /app/frontend/dist ./static

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
