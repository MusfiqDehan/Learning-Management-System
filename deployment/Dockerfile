# Use official Python 3.13 slim image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Copy requirements.txt first
COPY requirements.txt /app/

# Install curl + build deps, then uv
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl build-essential \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && export PATH="/root/.local/bin:$PATH" \
    && uv self update \
    && uv pip install --system --no-cache -r requirements.txt \
    && apt-get purge -y curl build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . /app/

# Collect static files
# RUN python manage.py collectstatic --noinput

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]