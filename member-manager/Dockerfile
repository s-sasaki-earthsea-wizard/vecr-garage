FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Create necessary directories
RUN mkdir -p /app/static /app/media

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
