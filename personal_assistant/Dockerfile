FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir fastapi uvicorn pydantic

# Explicitly install groq 0.4.0
RUN pip install --no-cache-dir groq==0.4.0

# Copy only what we need
COPY cloud_run_fixed.py .

# Debug: Print pip packages
RUN pip list

ENV PORT=8080
EXPOSE 8080

# Run our fixed implementation
CMD ["python", "cloud_run_fixed.py"] 