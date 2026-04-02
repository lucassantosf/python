import csv
import io
from typing import List
from src.modules.posts.repository import PostRepository
from src.modules.posts.domain import Post
from src.core.domain.exceptions import NotFoundException


class PostService:
    def __init__(self, post_repo: PostRepository):
        self.post_repo = post_repo

    def get_all(self) -> List[Post]:
        return self.post_repo.get_all()

    def get_by_id(self, post_id: int) -> Post:
        post = self.post_repo.get_by_id(post_id)
        if not post:
            raise NotFoundException("Post não encontrado")
        return post

    def create(self, title: str, content: str, author_id: int) -> Post:
        return self.post_repo.create(title=title, content=content, author_id=author_id)

    def update(self, post_id: int, title: str, content: str, author_id: int) -> Post:
        post = self.post_repo.get_by_id(post_id)
        if not post:
            raise NotFoundException("Post não encontrado")
        if post.author_id != author_id:
            raise NotFoundException("Post não encontrado ou sem permissão")
        updated = self.post_repo.update(post_id=post_id, title=title, content=content)
        if not updated:
            raise NotFoundException("Post não encontrado")
        return updated

    def delete(self, post_id: int, author_id: int) -> None:
        post = self.post_repo.get_by_id(post_id)
        if not post:
            raise NotFoundException("Post não encontrado")
        if post.author_id != author_id:
            raise NotFoundException("Post não encontrado ou sem permissão")
        self.post_repo.delete(post_id)

    # ------------------------------------------------------------------
    # CSV Import / Export
    # ------------------------------------------------------------------

    def import_from_csv(self, file_content: bytes) -> int:
        """
        Parses a CSV file (bytes) and bulk-inserts rows as posts.

        Expected columns: title, content, author_id
        Returns the number of successfully imported records.
        """
        text = file_content.decode("utf-8", errors="replace")
        reader = csv.DictReader(io.StringIO(text))

        required_fields = {"title", "content", "author_id"}
        posts: List[dict] = []
        for row in reader:
            if not required_fields.issubset(row.keys()):
                raise ValueError(
                    f"CSV inválido. Colunas obrigatórias: {', '.join(required_fields)}"
                )
            posts.append({
                "title": row["title"].strip(),
                "content": row["content"].strip(),
                "author_id": int(row["author_id"].strip()),
            })

        if not posts:
            return 0

        return self.post_repo.bulk_create(posts)

    def export_to_csv(self) -> bytes:
        """
        Exports all posts as a UTF-8 encoded CSV byte string.

        Columns: id, title, content, author_id
        """
        posts = self.post_repo.get_all_as_dicts()
        output = io.StringIO()
        fieldnames = ["id", "title", "content", "author_id"]
        writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(posts)
        return output.getvalue().encode("utf-8")
