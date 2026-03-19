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
