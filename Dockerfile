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

# Buka akses port 5000
EXPOSE 5000

# Jalankan server menggunakan Gunicorn dan arahkan ke 0.0.0.0
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]