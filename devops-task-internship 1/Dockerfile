FROM python:3.11-slim

# Create non-root user early
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /code

# Copy and install deps first — cached unless requirements change
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Switch to non-root
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
