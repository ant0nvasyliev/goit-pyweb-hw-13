FROM python:3.12

# Встановлення залежностей
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install --no-cache-dir poetry && \
    poetry install --no-root --no-interaction --no-ansi

# Копіюємо код програми
COPY . .

# Відкриваємо порт для FastAPI
EXPOSE 8000

# Запуск FastAPI з режимом перезавантаження
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]