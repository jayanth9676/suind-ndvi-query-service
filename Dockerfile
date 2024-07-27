# Use a multi-stage build to keep the final image small

# Stage 1: Build the frontend
FROM python:3.11-slim AS build-stage

WORKDIR /app

# Copy frontend files
COPY frontend/ /app/frontend/

# Install a lightweight HTTP server
RUN pip install httpserver

# Stage 2: Build the backend
FROM python:3.11-slim AS runtime-stage

WORKDIR /app

# Copy backend files
COPY main.py /app/
COPY sentinel_query.py /app/
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend files from the build stage
COPY --from=build-stage /app/frontend /app/frontend

# Expose port for FastAPI
EXPOSE 8000

# Start both the backend and frontend servers
CMD ["sh", "-c", "python -m uvicorn main:app --host 0.0.0.0 --port 8000 & python -m http.server --directory /app/frontend --bind 0.0.0.0 8080"]
