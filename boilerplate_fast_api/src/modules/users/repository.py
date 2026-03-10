from abc import ABC, abstractmethod
from typing import Any

class UserRepository(ABC):
    @abstractmethod
    def get_by_email(self, email: str) -> Any:
        pass

    @abstractmethod
    def get_by_id(self, user_id: Any) -> Any:
        pass
