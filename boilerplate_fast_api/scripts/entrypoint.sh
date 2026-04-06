#!/bin/sh

# Se DATABASE_URL for SQLite, não precisamos esperar
# Caso for Postgres, seria interessante um check aqui
case "$DATABASE_URL" in
  *postgres*)
    echo "Aguardando conexão com o Banco de Dados (PostgreSQL)..."
    # Adicione lógica de espera se necessário
    ;;
esac

echo "🚀 Aplicando migrações do banco de dados (Alembic)..."
alembic upgrade head

echo "🌱 Semeando dados (seed)..."
python scripts/seed_db.py

echo "🔥 Iniciando aplicação..."
exec "$@"
