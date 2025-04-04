FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Install required system dependencies, and remove cache
RUN apt-get update && apt-get install -y \
    build-essential \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install required Python dependencies, and remove cache
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache/pip && \
    rm requirements.txt

# Copy the source code and Makefile into the container
COPY src/ ./src/
COPY Makefile ./

# Set the entrypoint (This is just a placeholder)
ENTRYPOINT ["python", "src/app.py"]