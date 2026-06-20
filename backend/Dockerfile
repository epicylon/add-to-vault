FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY ./app ./app

# Run the Uvicorn server (FastAPI) without --reload for production stability
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
