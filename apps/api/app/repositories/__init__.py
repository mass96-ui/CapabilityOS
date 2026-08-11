"""
CapabilityOS Repository Layer.

Repositories encapsulate all database access logic.

Business services must never interact directly with SQLAlchemy.
Instead, they should depend on repository classes to perform
CRUD operations and queries.

Repository Pattern Benefits
---------------------------
- Separation of concerns
- Easier testing
- Cleaner business logic
- Database abstraction
"""

from app.repositories.base import BaseRepository
from app.repositories.user import UserRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
]