from typing import List, Optional
from sqlalchemy.orm import Session
from src.modules.posts.repository import PostRepository
from src.modules.posts.domain import Post
from src.infrastructure.database.models.post_model import PostModel


class PostSQLAlchemyRepository(PostRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[Post]:
        post_models = self.session.query(PostModel).all()
        return [
            Post(id=p.id, title=p.title, content=p.content, author_id=p.author_id)
            for p in post_models
        ]

    def get_by_id(self, post_id: int) -> Optional[Post]:
        post_model = self.session.query(PostModel).filter(PostModel.id == post_id).first()
        if post_model:
            return Post(
                id=post_model.id,
                title=post_model.title,
                content=post_model.content,
                author_id=post_model.author_id,
            )
        return None

    def create(self, title: str, content: str, author_id: int) -> Post:
        post_model = PostModel(title=title, content=content, author_id=author_id)
        self.session.add(post_model)
        self.session.commit()
        self.session.refresh(post_model)
        return Post(
            id=post_model.id,
            title=post_model.title,
            content=post_model.content,
            author_id=post_model.author_id,
        )

    def update(self, post_id: int, title: str, content: str) -> Optional[Post]:
        post_model = self.session.query(PostModel).filter(PostModel.id == post_id).first()
        if not post_model:
            return None
        post_model.title = title
        post_model.content = content
        self.session.commit()
        self.session.refresh(post_model)
        return Post(
            id=post_model.id,
            title=post_model.title,
            content=post_model.content,
            author_id=post_model.author_id,
        )

    def delete(self, post_id: int) -> bool:
        post_model = self.session.query(PostModel).filter(PostModel.id == post_id).first()
        if not post_model:
            return False
        self.session.delete(post_model)
        self.session.commit()
        return True

    def bulk_create(self, posts: List[dict]) -> int:
        """Inserts multiple posts in a single transaction. Returns count of created records."""
        post_models = [
            PostModel(
                title=p["title"],
                content=p["content"],
                author_id=int(p["author_id"]),
            )
            for p in posts
        ]
        self.session.add_all(post_models)
        self.session.commit()
        return len(post_models)

    def get_all_as_dicts(self) -> List[dict]:
        """Returns all posts as plain dicts for easy CSV serialization."""
        post_models = self.session.query(PostModel).all()
        return [
            {"id": p.id, "title": p.title, "content": p.content, "author_id": p.author_id}
            for p in post_models
        ]
