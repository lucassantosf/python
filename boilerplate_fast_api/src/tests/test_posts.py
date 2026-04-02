"""
test_posts.py — Suite de testes de integração para o módulo Posts.

Cobre:
  CRUD básico
    [GET /]   test_list_posts_empty
    [GET /]   test_list_posts_returns_created_post
    [GET /:id] test_get_post_by_id_success
    [GET /:id] test_get_post_not_found
    [POST /]  test_create_post_success
    [POST /]  test_create_post_missing_title
    [POST /]  test_create_post_missing_content
    [POST /]  test_create_post_missing_both_fields
    [POST /]  test_create_post_requires_auth
    [PUT /:id] test_update_post_success
    [PUT /:id] test_update_post_not_found
    [PUT /:id] test_update_post_ownership_violation
    [PUT /:id] test_update_post_requires_auth
    [DELETE /:id] test_delete_post_success
    [DELETE /:id] test_delete_post_not_found
    [DELETE /:id] test_delete_post_ownership_violation
    [DELETE /:id] test_delete_post_requires_auth

  CSV Import
    [POST /import-csv] test_import_csv_success
    [POST /import-csv] test_import_csv_multiple_rows
    [POST /import-csv] test_import_csv_invalid_extension
    [POST /import-csv] test_import_csv_missing_column
    [POST /import-csv] test_import_csv_empty_file
    [POST /import-csv] test_import_csv_requires_auth

  CSV Export
    [GET /export-csv] test_export_csv_empty_database
    [GET /export-csv] test_export_csv_with_posts
    [GET /export-csv] test_export_csv_content_type_header
    [GET /export-csv] test_export_csv_disposition_header
    [GET /export-csv] test_export_csv_is_public
"""

import io
import csv


# =============================================================================
# Helpers
# =============================================================================

def parse_csv_response(content: bytes) -> list[dict]:
    """Parseia bytes de CSV e retorna lista de dicts."""
    text = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))
    return list(reader)


# =============================================================================
# GET / — List posts
# =============================================================================

class TestListPosts:
    def test_list_posts_empty(self, client):
        """Deve retornar lista vazia quando não há posts."""
        response = client.get("/api/v1/posts/")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_posts_returns_created_post(self, client, created_post):
        """Deve retornar o post criado na fixture."""
        response = client.get("/api/v1/posts/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        ids = [p["id"] for p in data]
        assert created_post["id"] in ids

    def test_list_posts_contains_expected_fields(self, client, created_post):
        """Cada item deve conter os campos id, title, content e author_id."""
        response = client.get("/api/v1/posts/")
        assert response.status_code == 200
        post = response.json()[0]
        assert "id" in post
        assert "title" in post
        assert "content" in post
        assert "author_id" in post


# =============================================================================
# GET /{post_id} — Get single post
# =============================================================================

class TestGetPostById:
    def test_get_post_by_id_success(self, client, created_post):
        """Deve retornar 200 com o post correto."""
        post_id = created_post["id"]
        response = client.get(f"/api/v1/posts/{post_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == post_id
        assert data["title"] == created_post["title"]
        assert data["content"] == created_post["content"]

    def test_get_post_not_found(self, client):
        """Deve retornar 404 quando o post não existe."""
        response = client.get("/api/v1/posts/999999")
        assert response.status_code == 404

    def test_get_post_not_found_message(self, client):
        """A mensagem de erro do 404 deve ser descritiva."""
        response = client.get("/api/v1/posts/999999")
        assert "detail" in response.json()


# =============================================================================
# POST / — Create post
# =============================================================================

class TestCreatePost:
    def test_create_post_success(self, client, auth_headers, test_user):
        """Deve criar post e retornar 201 com campos corretos."""
        payload = {"title": "Novo Post", "content": "Conteúdo aqui"}
        response = client.post("/api/v1/posts/", json=payload, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Novo Post"
        assert data["content"] == "Conteúdo aqui"
        assert data["author_id"] == test_user["id"]
        assert "id" in data

    def test_create_post_missing_title(self, client, auth_headers):
        """Deve retornar 422 quando title está ausente."""
        response = client.post(
            "/api/v1/posts/",
            json={"content": "Sem título"},
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_create_post_missing_content(self, client, auth_headers):
        """Deve retornar 422 quando content está ausente."""
        response = client.post(
            "/api/v1/posts/",
            json={"title": "Sem conteúdo"},
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_create_post_missing_both_fields(self, client, auth_headers):
        """Deve retornar 422 quando ambos os campos estão ausentes."""
        response = client.post("/api/v1/posts/", json={}, headers=auth_headers)
        assert response.status_code == 422
        errors = response.json()["errors"]
        fields_with_error = [e["field"] for e in errors]
        assert "title" in fields_with_error
        assert "content" in fields_with_error

    def test_create_post_requires_auth(self, client):
        """Deve retornar 401/403 quando nenhum token é enviado."""
        response = client.post(
            "/api/v1/posts/",
            json={"title": "Sem auth", "content": "X"},
        )
        assert response.status_code in (401, 403)

    def test_create_post_invalid_token(self, client):
        """Deve retornar 401 com token inválido."""
        response = client.post(
            "/api/v1/posts/",
            json={"title": "Token inválido", "content": "X"},
            headers={"Authorization": "Bearer token_invalido"},
        )
        assert response.status_code == 401


# =============================================================================
# PUT /{post_id} — Update post
# =============================================================================

class TestUpdatePost:
    def test_update_post_success(self, client, auth_headers, created_post):
        """Deve atualizar o post e retornar os novos dados."""
        post_id = created_post["id"]
        payload = {"title": "Título Atualizado", "content": "Conteúdo atualizado"}
        response = client.put(
            f"/api/v1/posts/{post_id}",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Título Atualizado"
        assert data["content"] == "Conteúdo atualizado"

    def test_update_post_not_found(self, client, auth_headers):
        """Deve retornar 404 quando o post não existe."""
        response = client.put(
            "/api/v1/posts/999999",
            json={"title": "X", "content": "Y"},
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_update_post_ownership_violation(self, client, db_session, created_post):
        """Outro usuário não pode editar o post — deve retornar 404 (sem vazar existência)."""
        from sqlalchemy import text
        from src.infrastructure.security.jwt import JWTProvider

        # Cria um segundo usuário
        db_session.execute(
            text("INSERT INTO users (email, password_hash, role) VALUES (:e, :p, :r)"),
            {"e": "other@example.com", "p": "pw", "r": "user"},
        )
        db_session.commit()
        other_id = db_session.execute(
            text("SELECT id FROM users WHERE email='other@example.com'")
        ).fetchone()[0]

        other_token = JWTProvider.create_access_token(data={"sub": str(other_id)})
        other_headers = {"Authorization": f"Bearer {other_token}"}

        response = client.put(
            f"/api/v1/posts/{created_post['id']}",
            json={"title": "Invasão", "content": "X"},
            headers=other_headers,
        )
        assert response.status_code == 404

    def test_update_post_requires_auth(self, client, created_post):
        """Deve retornar 401/403 sem token."""
        response = client.put(
            f"/api/v1/posts/{created_post['id']}",
            json={"title": "X", "content": "Y"},
        )
        assert response.status_code in (401, 403)

    def test_update_post_missing_title(self, client, auth_headers, created_post):
        """Deve retornar 422 quando title está ausente no payload de atualização."""
        response = client.put(
            f"/api/v1/posts/{created_post['id']}",
            json={"content": "Sem título"},
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_update_post_missing_content(self, client, auth_headers, created_post):
        """Deve retornar 422 quando content está ausente no payload de atualização."""
        response = client.put(
            f"/api/v1/posts/{created_post['id']}",
            json={"title": "Sem conteúdo"},
            headers=auth_headers,
        )
        assert response.status_code == 422


# =============================================================================
# DELETE /{post_id} — Delete post
# =============================================================================

class TestDeletePost:
    def test_delete_post_success(self, client, auth_headers, created_post):
        """Deve remover o post e retornar 204 sem corpo."""
        post_id = created_post["id"]
        response = client.delete(f"/api/v1/posts/{post_id}", headers=auth_headers)
        assert response.status_code == 204
        assert response.content == b""

    def test_delete_post_confirms_removal(self, client, auth_headers, created_post):
        """Após deletar, GET do post deve retornar 404."""
        post_id = created_post["id"]
        client.delete(f"/api/v1/posts/{post_id}", headers=auth_headers)
        response = client.get(f"/api/v1/posts/{post_id}")
        assert response.status_code == 404

    def test_delete_post_not_found(self, client, auth_headers):
        """Deve retornar 404 quando o post não existe."""
        response = client.delete("/api/v1/posts/999999", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_post_ownership_violation(self, client, db_session, created_post):
        """Outro usuário não pode deletar o post — deve retornar 404."""
        from sqlalchemy import text
        from src.infrastructure.security.jwt import JWTProvider

        db_session.execute(
            text("INSERT INTO users (email, password_hash, role) VALUES (:e, :p, :r)"),
            {"e": "attacker@example.com", "p": "pw", "r": "user"},
        )
        db_session.commit()
        attacker_id = db_session.execute(
            text("SELECT id FROM users WHERE email='attacker@example.com'")
        ).fetchone()[0]

        attacker_token = JWTProvider.create_access_token(data={"sub": str(attacker_id)})
        response = client.delete(
            f"/api/v1/posts/{created_post['id']}",
            headers={"Authorization": f"Bearer {attacker_token}"},
        )
        assert response.status_code == 404

    def test_delete_post_requires_auth(self, client, created_post):
        """Deve retornar 401/403 sem token."""
        response = client.delete(f"/api/v1/posts/{created_post['id']}")
        assert response.status_code in (401, 403)


# =============================================================================
# POST /import-csv — Import posts
# =============================================================================

class TestImportCsv:
    def _make_csv_file(self, rows: list[dict]) -> tuple:
        """Gera bytes de CSV e retorno para usar com files= do TestClient."""
        output = io.StringIO()
        writer = csv.DictWriter(
            output, fieldnames=["title", "content", "author_id"], lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
        content = output.getvalue().encode("utf-8")
        return ("file", ("posts.csv", io.BytesIO(content), "text/csv"))

    def test_import_csv_success(self, client, auth_headers, test_user):
        """Deve importar 1 post e retornar mensagem de sucesso com contagem."""
        rows = [{"title": "CSV Post", "content": "Conteúdo CSV", "author_id": test_user["id"]}]
        response = client.post(
            "/api/v1/posts/import-csv",
            headers=auth_headers,
            files=[self._make_csv_file(rows)],
        )
        assert response.status_code == 201
        assert "1 post(s) importado(s)" in response.json()["message"]

    def test_import_csv_multiple_rows(self, client, auth_headers, test_user):
        """Deve importar múltiplos posts e retornar contagem correta."""
        rows = [
            {"title": f"Post {i}", "content": f"Conteúdo {i}", "author_id": test_user["id"]}
            for i in range(3)
        ]
        response = client.post(
            "/api/v1/posts/import-csv",
            headers=auth_headers,
            files=[self._make_csv_file(rows)],
        )
        assert response.status_code == 201
        assert "3 post(s) importado(s)" in response.json()["message"]

    def test_import_csv_posts_appear_in_list(self, client, auth_headers, test_user):
        """Posts importados devem aparecer no GET /posts/."""
        rows = [{"title": "Importado", "content": "Via CSV", "author_id": test_user["id"]}]
        client.post(
            "/api/v1/posts/import-csv",
            headers=auth_headers,
            files=[self._make_csv_file(rows)],
        )
        list_response = client.get("/api/v1/posts/")
        titles = [p["title"] for p in list_response.json()]
        assert "Importado" in titles

    def test_import_csv_invalid_extension(self, client, auth_headers):
        """Deve retornar 422 quando o arquivo não tem extensão .csv."""
        response = client.post(
            "/api/v1/posts/import-csv",
            headers=auth_headers,
            files=[("file", ("posts.txt", io.BytesIO(b"title,content,author_id\n"), "text/plain"))],
        )
        assert response.status_code == 422

    def test_import_csv_missing_required_column(self, client, auth_headers):
        """Deve retornar 422 quando o CSV não tem todas as colunas obrigatórias."""
        # CSV sem coluna author_id
        bad_csv = b"title,content\nPost sem autor,Conteudo\n"
        response = client.post(
            "/api/v1/posts/import-csv",
            headers=auth_headers,
            files=[("file", ("posts.csv", io.BytesIO(bad_csv), "text/csv"))],
        )
        assert response.status_code == 422

    def test_import_csv_empty_file_returns_zero(self, client, auth_headers):
        """Um CSV com apenas cabeçalho (sem dados) deve importar 0 posts."""
        empty_csv = b"title,content,author_id\n"
        response = client.post(
            "/api/v1/posts/import-csv",
            headers=auth_headers,
            files=[("file", ("posts.csv", io.BytesIO(empty_csv), "text/csv"))],
        )
        assert response.status_code == 201
        assert "0 post(s)" in response.json()["message"]

    def test_import_csv_requires_auth(self, client, test_user):
        """Deve retornar 401/403 sem token de autenticação."""
        rows = [{"title": "No Auth", "content": "X", "author_id": test_user["id"]}]
        response = client.post(
            "/api/v1/posts/import-csv",
            files=[self._make_csv_file(rows)],
        )
        assert response.status_code in (401, 403)


# =============================================================================
# GET /export-csv — Export posts
# =============================================================================

class TestExportCsv:
    def test_export_csv_is_public(self, client):
        """Rota de export deve ser pública (sem autenticação)."""
        response = client.get("/api/v1/posts/export-csv")
        assert response.status_code == 200

    def test_export_csv_empty_database(self, client):
        """Exportar sem posts deve retornar apenas o cabeçalho CSV."""
        response = client.get("/api/v1/posts/export-csv")
        assert response.status_code == 200
        rows = parse_csv_response(response.content)
        assert rows == []

    def test_export_csv_content_type_header(self, client):
        """Content-Type deve ser text/csv."""
        response = client.get("/api/v1/posts/export-csv")
        assert "text/csv" in response.headers["content-type"]

    def test_export_csv_disposition_header(self, client):
        """Content-Disposition deve indicar download do arquivo posts.csv."""
        response = client.get("/api/v1/posts/export-csv")
        disposition = response.headers.get("content-disposition", "")
        assert "attachment" in disposition
        assert "posts.csv" in disposition

    def test_export_csv_with_posts(self, client, created_post):
        """Deve incluir o post criado nos dados exportados."""
        response = client.get("/api/v1/posts/export-csv")
        assert response.status_code == 200
        rows = parse_csv_response(response.content)
        assert len(rows) >= 1

    def test_export_csv_has_correct_columns(self, client, created_post):
        """O CSV deve conter as colunas id, title, content, author_id."""
        response = client.get("/api/v1/posts/export-csv")
        rows = parse_csv_response(response.content)
        assert len(rows) >= 1
        first = rows[0]
        assert "id" in first
        assert "title" in first
        assert "content" in first
        assert "author_id" in first

    def test_export_csv_data_matches_post(self, client, created_post):
        """Os dados exportados devem corresponder ao post criado."""
        response = client.get("/api/v1/posts/export-csv")
        rows = parse_csv_response(response.content)
        post_row = next(
            (r for r in rows if int(r["id"]) == created_post["id"]), None
        )
        assert post_row is not None
        assert post_row["title"] == created_post["title"]
        assert post_row["content"] == created_post["content"]
        assert int(post_row["author_id"]) == created_post["author_id"]

    def test_export_csv_round_trip(self, client, auth_headers, test_user):
        """Import seguido de export deve preservar os dados (round-trip)."""
        import_rows = [
            {"title": "Round Trip", "content": "Dados preservados", "author_id": test_user["id"]}
        ]
        output = io.StringIO()
        writer = csv.DictWriter(
            output, fieldnames=["title", "content", "author_id"], lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(import_rows)
        csv_bytes = output.getvalue().encode("utf-8")

        client.post(
            "/api/v1/posts/import-csv",
            headers=auth_headers,
            files=[("file", ("posts.csv", io.BytesIO(csv_bytes), "text/csv"))],
        )

        response = client.get("/api/v1/posts/export-csv")
        rows = parse_csv_response(response.content)
        round_trip = next((r for r in rows if r["title"] == "Round Trip"), None)
        assert round_trip is not None
        assert round_trip["content"] == "Dados preservados"
