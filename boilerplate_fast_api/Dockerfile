# ========================================
# 🐳 Dockerfile Multi-stage para FastAPI
# ========================================

# -- Estágio de Build --
FROM python:3.12-slim as builder

# Define variáveis de ambiente úteis
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Instala ferramentas essenciais para bibliotecas nativas (ex: se usar psycopg2 ao invés de binary)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Prepara ambiente virtual para instalação
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instala as dependências do projeto
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -- Estágio Final --
FROM python:3.12-slim

WORKDIR /app

# Define ambiente virtual e path
ENV PATH="/opt/venv/bin:$PATH"
COPY --from=builder /opt/venv /opt/venv

# Expõe a porta do uvicorn
EXPOSE 8000

# Copia o código fonte
COPY . .

# Garante permissão de execução do entrypoint
RUN chmod +x ./scripts/entrypoint.sh

# Variáveis padrão (podem ser sobrescritas no docker-compose)
ENV DATABASE_URL="sqlite:///./app.db"
ENV SECRET_KEY="sua-chave-super-secreta"

# Inicia via script (usando sh para garantir execução independente de permissões no host volume)
ENTRYPOINT ["sh", "./scripts/entrypoint.sh"]

# Comando padrão
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
