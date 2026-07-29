import uuid

from backend.app.api.schemas.user import UserCreate, UserUpdate
from backend.app.core.exceptions import ConflictException, UnauthorizedException
from backend.app.core.security import hash_password, verify_password
from backend.app.models.user import User
from backend.app.services.base import BaseService
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


class UserService(BaseService[User, UserUpdate]):
    """CRUD for User, extending BaseService with password hashing and the
    email-uniqueness rule. Reuses get_by_id / get_all / delete as-is."""

    model = User

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def authenticate(self, email: str, password: str) -> User:
        """Return the user for these credentials, or raise 401.

        The same error is used for unknown email, wrong password and inactive
        account so a caller can't probe which emails exist.
        """
        user = await self.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Incorrect email or password")
        if not user.is_active:
            raise UnauthorizedException("Incorrect email or password")
        return user

    async def create_user(self, data: UserCreate) -> User:
        user = User(email=data.email, hashed_password=hash_password(data.password))
        try:
            return await self.create(user)
        except IntegrityError as exc:
            raise ConflictException("A user with this email already exists") from exc

    async def update_user(self, id: uuid.UUID, data: UserUpdate) -> User:
        user = await self.get_by_id(id)

        fields = data.model_dump(exclude_unset=True)
        if "password" in fields:
            user.hashed_password = hash_password(fields.pop("password"))
        for field, value in fields.items():
            setattr(user, field, value)

        try:
            await self.db.flush()
        except IntegrityError as exc:
            raise ConflictException("A user with this email already exists") from exc
        return user
