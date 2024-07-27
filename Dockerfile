# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Create and set the working directory
WORKDIR /app

# Copy the backend files
COPY main.py sentinel_query.py requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the frontend files
COPY frontend /app/frontend

# Expose the port the app runs on
EXPOSE 8000

# Install an HTTP server to serve the frontend
RUN apt-get update && apt-get install -y \
    python3-venv \
    && python3 -m venv /venv \
    && /venv/bin/pip install --no-cache-dir http.server

# Start both the backend and frontend server
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000 & python3 -m http.server --directory /app/frontend 5500"]
