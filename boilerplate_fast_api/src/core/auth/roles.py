from enum import Enum
from typing import List
from src.core.auth.permissions import Permission

class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"

# Mapping which roles have which permissions
ROLE_PERMISSIONS = {
    Role.USER: [
        Permission.READ_POSTS
    ],
    Role.ADMIN: [
        Permission.READ_USERS,
        Permission.WRITE_USERS,
        Permission.READ_POSTS,
        Permission.WRITE_POSTS,
    ]
}

def get_role_permissions(role: str) -> List[Permission]:
    """Returns the list of permissions associated with the chosen role"""
    try:
        return ROLE_PERMISSIONS.get(Role(role), [])
    except ValueError:
        return []
