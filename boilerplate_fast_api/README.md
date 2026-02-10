
Files and folders' hierarchy 

src/
├── api/
│   ├── routes/
│   │   ├── auth.py
│   │   ├── posts.py
│   │   └── users.py
│   │
│   ├── dependencies/
│   │   ├── auth.py
│   │   ├── acl.py
│   │   └── db.py
│   │
│   ├── middlewares/
│   │   └── request_context.py
│   │
│   └── error_handlers.py
│
├── core/
│   ├── domain/
│   │   ├── base_entity.py
│   │   └── exceptions.py
│   │
│   ├── auth/
│   │   ├── roles.py
│   │   └── permissions.py
│   │
│   └── shared/
│       └── result.py
│
├── modules/
│   ├── auth/
│   │   ├── domain.py
│   │   ├── service.py
│   │   ├── schemas.py
│   │   └── dependencies.py
│   │
│   ├── users/
│   │   ├── domain.py
│   │   ├── repository.py
│   │   ├── service.py
│   │   └── schemas.py
│   │
│   └── posts/
│       ├── domain.py
│       ├── repository.py
│       ├── service.py
│       └── schemas.py
│
├── infrastructure/
│   ├── database/
│   │   ├── base.py
│   │   └── session.py
│   │
│   ├── repositories/
│   │   ├── user_sqlalchemy.py
│   │   └── post_sqlalchemy.py
│   │
│   ├── security/
│   │   ├── jwt.py
│   │   └── password.py
│   │
│   └── tasks/
│       ├── jobs.py
│       └── exports.py
│
├── tests/
│   ├── unit/
│   │   ├── posts/
│   │   └── users/
│   │
│   └── integration/
│       └── api/
│
├── settings.py
└── main.py


# Execuing the api locally

## If not, create the virtual environment

python -m venv .venv

## Activate it 

. .venv/bin/activate

## Install dependencies


pip install -r requirements.txt

## Execute the api

uvicorn src.main:app --reload

# Python + FastApi - Boilerplate

[] - Auth with JWT

[] - Dockerfiles

[] - Acl

[] - Model Base to extend other models

[] - CRUD Example (Post) based on model example

[] - Exports example

[] - Jobs example

[] - Commands example

    The commands files are located at /app/Console/Commands/

    The scheduler is at routes/console.php

[] - Tests Coverage example

    First, execute mysql container only:

    sudo docker compose up -d mysql

    After, execute phpunit 

    ./vendor/bin/phpunit