from enum import Enum

class Permission(str, Enum):
    # General list of strict system permissions
    READ_USERS = "read:users"
    WRITE_USERS = "write:users"
    READ_POSTS = "read:posts"
    WRITE_POSTS = "write:posts"
