# ============================
#       BUILDER
# ============================
FROM python:3.12-slim AS builder

# Обновления и зависимости для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установка uv
RUN pip install uv

WORKDIR /app

# Сначала копируем зависимости
COPY pyproject.toml ./
COPY uv.lock ./

# Устанавливаем зависимости в системный Python
RUN uv pip install --system --compile .

# Затем копируем исходный код
COPY . .

# ============================
#       RUNTIME
# ============================
FROM python:3.12-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем установленную среду из builder
COPY --from=builder /usr/local /usr/local
COPY --from=builder /app /app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]