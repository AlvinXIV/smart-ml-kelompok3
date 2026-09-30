FROM python:3.11-slim

# Mencegah Python membuat file .pyc dan memastikan output langsung ke console
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Tambahkan libpq-dev untuk dependency driver PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependency Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin source code
COPY . .

# Buat folder data jika belum ada
RUN mkdir -p /app/data

EXPOSE 5000

# Jalankan server
CMD ["python", "run.py"]