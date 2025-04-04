FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install required Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the source code
COPY src/ ./src/

# Set the entrypoint
ENTRYPOINT ["python", "src/app.py"]