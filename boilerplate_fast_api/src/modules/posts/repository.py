from abc import ABC, abstractmethod
from typing import Any, List, Optional


class PostRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Any]:
        pass

    @abstractmethod
    def get_by_id(self, post_id: Any) -> Optional[Any]:
        pass

    @abstractmethod
    def create(self, title: str, content: str, author_id: int) -> Any:
        pass

    @abstractmethod
    def update(self, post_id: Any, title: str, content: str) -> Optional[Any]:
        pass

    @abstractmethod
    def delete(self, post_id: Any) -> bool:
        pass
