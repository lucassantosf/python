# 🚀 Python + FastAPI - Clean Architecture Boilerplate

Este é um boilerplate robusto para construção de APIs usando **Python** e **FastAPI**. Seu objetivo é fornecer um ponto de partida altamente escalável e de fácil manutenção.

## 🧠 Filosofia e Estratégia da Arquitetura

O projeto utiliza uma arquitetura pragmática focada na **separação rigorosa de interesses (Separation of Concerns)**. Ao invés de misturar regras de negócio com ferramentas, combinamos os melhores conceitos de:

- **Domain Driven Design (Pragmático):** A aplicação é desenhada e agrupada ao redor dos contextos de negócios (ex: `users` e `auth`), não de tipos de arquivos.
- **Arquitetura Hexagonal (Ports and Adapters):** O "coração" da aplicação desconhece se está usando um banco PostgreSQL, SQLite, se recebe chamadas HTTP ou de terminal. A tecnologia entra como plugin nas bordas do sistema.
- **Repository e Service Pattern:** Lógica bruta na camada de Serviço, persistência através de contratos na camada de Repositório.
- **Dependency Injection (Injeção de Dependências):** Utilizada intensamente para injetar bancos de dados ou serviços nos roteadores e instanciar classes de forma desacoplada.

**A regra de ouro aqui é:** *Se o FastAPI, o SQLAlchemy ou o JWT deixarem de existir ou precisarem ser substituídos amanhã, 90% do seu código permanecerá intacto, pois o domínio não conhece as ferramentas externas.*

---

## 🗂️ Estrutura de Diretórios e Arquivos

Abaixo está o mapeamento da estrutura de diretórios já preenchida e configurada no projeto base atual:

```text
src/
├── api/
│   ├── dependencies/
│   │   └── auth.py
│   ├── middlewares/
│   └── routes/
│       ├── auth.py
│       ├── health.py
│       ├── posts.py
│       └── users.py
├── core/
│   ├── auth/
│   └── domain/
│       └── exceptions.py
├── infrastructure/
│   ├── database/
│   │   ├── base.py
│   │   ├── migrations/
│   │   │   └── versions/
│   │   │       ├── 9f6394f59e10_create_users_table.py
│   │   │       ├── 4e476fafdd43_add_role_column_to_users.py
│   │   │       └── 2f7d4eb54e44_create_posts_table.py
│   │   ├── models/
│   │   │   ├── user_model.py
│   │   │   └── post_model.py
│   │   └── session.py
│   ├── repositories/
│   │   ├── user_sqlalchemy.py
│   │   └── post_sqlalchemy.py
│   ├── security/
│   │   ├── jwt.py
│   │   └── password.py
│   └── tasks/
├── modules/
│   ├── auth/
│   │   ├── dependencies.py
│   │   ├── schemas.py
│   │   └── service.py
│   ├── posts/
│   │   ├── dependencies.py
│   │   ├── domain.py
│   │   ├── repository.py
│   │   ├── schemas.py
│   │   └── service.py
│   └── users/
│       ├── dependencies.py
│       ├── domain.py
│       ├── repository.py
│       ├── schemas.py
│       └── service.py
├── tests/
├── main.py
└── settings.py
```

---

## 🏗️ Explicação das Camadas

### 1. `src/api/` (Camada HTTP / Inbound Adapters)
Esta camada lida exclusivamente com a interface web (Framework FastAPI) a fim de expor a aplicação. **Nenhuma** regra de negócio deve habitar aqui.
- **`routes/`**: Recebe a requisição (Endpoints), garante a autenticação, injeta os serviços necessários e retorna a resposta mapeada.
- **`dependencies/`**: Dependências utilitárias de intersecção específicas da camada HTTP, como extrair os payloads JWT da requisição atual.
- **`middlewares/`**: Middlewares para o ciclo de vida das requisições web.

### 2. `src/core/` (Core / Shared Domain)
Armazena domínios compartilhados (agnósticos de Framework de HTTP e Banco de Dados) base que cruzam transversalmente nossa aplicação.
- **`domain/`**: Entidades superclasses (Abstracts), assim como todas as Exceções (`DomainExceptions`) base de regra de negócios.
- **`auth/`**: Regras universais de permissão, como papéis (Roles) e lista de controle de acesso (ACL).

### 3. `src/modules/` (Application Layer / Business Logic)
A aplicação real. É dividida por contextos orgânicos (Módulos). Cada módulo deve ser coeso, auto contido sobre seu próprio assunto. Um módulo padrão (`users`, `auth`) contém:
- **`domain.py`**: Modelos puramente em Python, entidades e validações de estado do assunto. Sem SQLAlchemy ou Pydantic pesado guiando persistência.
- **`schemas.py`**: Modelos Pydantic (DTOs) que servem de contrato para as entradas e saídas exigidas pelos seus *controllers/routes*.
- **`service.py`**: (Service Layer) É o verdadeiro orquestrador do sistema. Executa regras, compara variáveis, checa exceções. Não acessa o banco diretamente, mas utiliza as interfaces.
- **`repository.py`**: A **interface/Contrato de Repository**, que dita o que o ambiente externo tem obrigação de salvar, consultar ou atualizar. O Serviço importa isso.
- **`dependencies.py`**: Contêineres de Injeção de Dependências que instanciam Serviços reais plugando um Banco de Dados na Interface abstrata do repositório a ser enviada para a Rota.

### 4. `src/infrastructure/` (Infraestrutura / Outbound Adapters)
É o único lugar do projeto que sabe como salvar em banco ou criptografar os dados. Este local **sabe da existência das bibliotecas** (FastAPI, SQLAlchemy, PyJWT, passlib, etc).
- **`database/`**: Configurações de conexão base da engine do SQL e configurações de migração (Alembic). Os `models/*.py` vivem ali contendo as marcações concretas do SQL.
- **`repositories/`**: Implementações reais dos contratos declarados em `modules/*/repository.py`. Aqui que orquestramos o `session.query` do SQLAlchemy, realizando os commits, filtros, etc.
- **`security/`**: Scripts e integrações técnicas reais, como o JWT in-memory blacklist, cifragem, e algoritmos bcrypt em Senhas.

### 5. `src/tests/` (Testes)
Testes garantirão que a segregação está funcionando. Mocks simples nos módulos do `service` são o foco de Testes Unitários, enquanto Testes de Integração varrerão o FastAPI até o Arquivo de SQLite rodando na máquina.

---

## 🏃‍♂️ Como rodar o projeto localmente

Siga os passos abaixo para configurar e ligar a API via `uvicorn`:

### 1. Criar e Ativar Ambiente Virtual
Se você não possui o ambiente montado na raiz do projeto, crie um:
```bash
python -m venv .venv

# No Linux / macOS:
source .venv/bin/activate
# No Windows:
.venv\Scripts\activate
```

### 2. Instalar as Dependências
Com o ambiente ativo, instale os pacotes definidos no projeto (FastAPI, SQLAlchemy, Alembic, uvicorn, JWT, etc):
```bash
pip install -r requirements.txt
```

### 3. Setup de Banco de Dados e Migrations
*Nota: a string de conexão configurada usa SQLite em arquivo (`app.db`) visando extrema agilidade no start inicial.*
Rode as migrações (criar tabelas via Alembic) no terminal:
```bash
alembic upgrade head
```

### 4. Executar a API Master
Suba o servidor e comece a efetuar chamadas a partir das rotas mapeadas no Insomnia/Postman:
```bash
uvicorn src.main:app --reload
```
A aplicação estará disponível em `http://127.0.0.1:8000/`. (Swagger Docs habilitado em `/docs`).

---

## 🗄️ Comandos de Migrations (Alembic)

As migrações de banco de dados são gerenciadas puramente atravé do **Alembic**. O ambiente e os scripts ficam armazenados em `src/infrastructure/database/migrations/`. 

Todos esses comandos devem ser executados a partir da **raiz do seu projeto**, onde residem o arquivo de suporte mestre chamado `alembic.ini`.

**Gerar migração após alterar models Python (`user_model.py`):**
```bash
alembic revision --autogenerate -m "sua mensagem descritiva aqui"
```
*(Importante: se for um arquivo model novo, importe-o no `env.py` do migration para o bot detectá-lo).*

**Aplicar as atualizações e criar/editar as tabelas de fato no banco:**
```bash
alembic upgrade head
```

**Reverter / Fazer Rollback (Desfazer última migration):**
```bash
alembic downgrade -1
```

---

## ✅ Boilerplate Checklist

[x] - Auth with JWT *(Pronto & testado em memória local)*

[x] - Endpoint `/users/me` *(Pronto)*

[x] - Setup Alembic Database Migrations *(Pronto)*

[x] - Setup DI Auth Repositories into Modules *(Pronto)*

[x] - CRUD Example (Posts) *(Pronto — ver seção abaixo)*

[x] - Custom global validation error handler *(Pronto — ver seção abaixo)*

[x] - Acl (Access Control Roles) *(Pronto — `Permission` enum, `Role` enum + `ROLE_PERMISSIONS` map, e `require_permissions()` dependency em uso)*

[x] - Jobs example (FastAPI BackgroundTasks) *(Pronto — endpoint `/api/v1/posts/generate`)*

[x] - Scheduler for periodic commands (APScheduler) *(Pronto - `src.infrastructure.tasks.scheduler` disparando job por minuto)*

[x] - Exports/Imports .csv examples *(Pronto — ver seção abaixo)*

[x] - Tests Coverage example with PyTest *(Pronto — ver seção abaixo)*

[] - Dockerfiles (API and possible Database image)

---

## 📝 CRUD de Posts

O módulo `posts` implementa um CRUD completo seguindo a mesma arquitetura dos demais módulos.

### Endpoints

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| `GET` | `/api/v1/posts/` | ❌ Público | Lista todos os posts |
| `GET` | `/api/v1/posts/{id}` | ❌ Público | Retorna um post pelo ID |
| `POST` | `/api/v1/posts/` | ✅ JWT | Cria um novo post (author_id extraído do token) |
| `POST` | `/api/v1/posts/generate` | ✅ JWT | Dispara um job em background (BackgroundTasks) para gerar um post falso |
| `PUT` | `/api/v1/posts/{id}` | ✅ JWT | Atualiza um post (somente o autor pode alterar) |
| `DELETE` | `/api/v1/posts/{id}` | ✅ JWT | Remove um post (somente o autor pode remover) |
| `POST` | `/api/v1/posts/import-csv` | ✅ JWT | Importa posts a partir de um arquivo `.csv` |
| `GET` | `/api/v1/posts/export-csv` | ❌ Público | Exporta todos os posts como arquivo `.csv` para download |

### Regra de Ownership

O `PostService` verifica se `post.author_id == current_user_id` antes de permitir atualizações ou exclusões. Qualquer violação retorna **404** para não vazar se o recurso existe.

### Arquivos criados

| Arquivo | Camada | Papel |
|---------|--------|-------|
| `modules/posts/domain.py` | Domínio | Modelo puro Python `Post` |
| `modules/posts/repository.py` | Módulo (Port) | Interface abstrata do repositório |
| `modules/posts/schemas.py` | Módulo (DTOs) | `PostCreate`, `PostUpdate`, `PostResponse` |
| `modules/posts/service.py` | Módulo (Serviço) | Regras de negócio e checagem de ownership |
| `modules/posts/dependencies.py` | Módulo (DI) | Injeta repositório concreto no serviço |
| `infrastructure/database/models/post_model.py` | Infra | SQLAlchemy model com FK para `users.id` |
| `infrastructure/repositories/post_sqlalchemy.py` | Infra (Adapter) | Implementação concreta do `PostRepository` |
| `infrastructure/tasks/post_tasks.py` | Infra | Job assíncrono isolado para geração de mock de posts |
| `api/routes/posts.py` | API (HTTP) | 8 endpoints REST (incluindo import/export CSV e dispatch de job) |

---

## 📂 Import / Export de Posts via CSV

Dois endpoints foram adicionados ao módulo `posts` para suportar carga e extração de dados em massa via arquivo `.csv`.

### Endpoints

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| `POST` | `/api/v1/posts/import-csv` | ✅ JWT | Importa posts a partir de um arquivo `.csv` (multipart/form-data) |
| `GET`  | `/api/v1/posts/export-csv` | ❌ Público | Exporta todos os posts da base como um arquivo `.csv` para download |

### Formato do CSV (import)

O arquivo `.csv` deve conter **obrigatoriamente** as colunas abaixo (cabeçalho na primeira linha):

```csv
title,content,author_id
Meu primeiro post,Conteúdo do post aqui.,1
Segundo post,Outro conteúdo.,1
```

- **Erros de coluna ausente** retornam `HTTP 422` com mensagem descritiva.
- **Arquivo sem extensão `.csv`** também retorna `HTTP 422`.
- Todos os registros são inseridos em **uma única transação** (`bulk_create`).

### Resposta (import — sucesso)

```json
{ "message": "3 post(s) importado(s) com sucesso." }
```

### Resposta (export)

Retorna diretamente o arquivo com header `Content-Disposition: attachment; filename=posts.csv` e `Content-Type: text/csv`.

---

## 🚨 Validação Global de Erros

Um handler global de `RequestValidationError` foi adicionado ao `main.py`. Ele intercepta todos os erros de validação do Pydantic em qualquer rota da aplicação e os transforma num formato limpo e consistente.

**Resposta padrão (HTTP 422):**
```json
{
  "errors": [
    { "field": "title",   "message": "This field is required." },
    { "field": "content", "message": "This field is required." }
  ]
}
```

- O prefixo `body` é removido do nome do campo (detalhe interno do Pydantic).
- Mensagens desconhecidas fazem fallback para `.capitalize() + "."`, garantindo que nenhum erro seja silenciado.
- O handler cobre **todos** os módulos presentes e futuros — nenhuma rota precisa tratar isso individualmente.

---

## 🧪 Testes Automatizados (PyTest)

O projeto conta com uma suite de testes de integração que utiliza um banco **SQLite em memória**, garantindo que os testes sejam rápidos, isolados e não afetem seu banco de dados local (`app.db`).

### O que está sendo testado?
No módulo de `posts`, cobrimos 100% das condições:
- **CRUD Completo:** Listagem, busca por ID, criação, atualização e deleção.
- **Segurança (Ownership):** Garante que apenas o autor pode editar/deletar seu próprio post.
- **Autenticação:** Valida se rotas protegidas exigem o token JWT.
- **Validação de Payload:** Testa campos obrigatórios e erros de formato (Pydantic).
- **Import/Export CSV:** Valida importação de múltiplas linhas, colunas obrigatórias e integridade dos dados no download.

### Como rodar os testes

1. Certifique-se de que as dependências de teste estão instaladas:
```bash
pip install -r requirements.txt
```

2. Execute o comando `pytest` na raiz do projeto:
```bash
pytest
```

#### Dicas Úteis:
- Para ver os nomes dos testes enquanto rodam: `pytest -v`
- Para parar no primeiro erro: `pytest -x`
- Para ver o print de depuração (se houver): `pytest -s`