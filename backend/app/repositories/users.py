"""UsersRepository — seller accounts."""

from typing import Optional

from sqlalchemy import select

from app.models import User
from app.repositories.base import BaseRepository


class UsersRepository(BaseRepository):
    def create(self, *, email: str, password_hash: str, name: str) -> User:
        """Add a user and flush (assigns user_id). Caller commits."""
        user = User(email=email, password_hash=password_hash, name=name)
        self.session.add(user)
        self.session.flush()
        return user

    def get_by_email(self, email: str) -> Optional[User]:
        return self.session.scalar(select(User).where(User.email == email))

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.session.get(User, user_id)
