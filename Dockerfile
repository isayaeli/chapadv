FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install basic build deps that you need for local dev (psycopg2 dev headers etc)
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source for one-off commands (but for active dev we'll mount host volume)
COPY . .


# Default dev command: run Django dev server (not for prod!)
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

RUN pip install gunicorn

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]

