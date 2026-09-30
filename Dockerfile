FROM python:3.11-slim

# Mencegah Python membuat file .pyc dan memastikan output langsung ke console
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependency sistem yang dibutuhkan untuk build library ML
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
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