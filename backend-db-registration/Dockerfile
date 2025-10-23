FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Install required system dependencies, and remove cache
RUN apt-get update && apt-get install -y \
    build-essential \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install required Python dependencies, and remove cache
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache/pip && \
    rm requirements.txt

# Copy the source code and Makefile into the container
COPY src/ ./src/
COPY tests/ ./tests/
COPY Makefile ./

# Set the PYTHONPATH to include the src directory
ENV PYTHONPATH="/app/src:$PYTHONPATH"

# Set the entrypoint to start the FastAPI application
ENTRYPOINT ["python", "src/app.py"]
