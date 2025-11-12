FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install required Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Set the PYTHONPATH to include the src directory
ENV PYTHONPATH="/app/src:$PYTHONPATH"

# Discord Bot起動コマンド
CMD ["python", "src/app.py"]
