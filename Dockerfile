# Dockerfile
FROM python:3.13-slim

WORKDIR /app

# Instalar dependências do sistema e Poetry
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir poetry

# Configurar Poetry
ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

# Copiar arquivos de dependências
COPY pyproject.toml poetry.lock* ./

# Instalar dependências
RUN poetry install --only=main --no-root

# Copiar código da aplicação
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Criar usuário não-root
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
