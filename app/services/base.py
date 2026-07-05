import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constant import DEFAULT_PAGE_SIZE
from app.core.exceptions import NotFoundException
from app.models.base import AppModel
from app.schemas.base import AppSchema


class BaseService[ModelT: AppModel, UpdateModelT: AppSchema]:
    """
    Generic CRUD service. Extend it and set `model` to get
    get_by_id / get_all / create / update / delete for free.

    Write methods only flush(); they never commit. The request-level
    transaction is committed (or rolled back) once in `get_db`, so multiple
    service calls within one request are atomic.

    Example:
        class UserService(BaseService[User, UserUpdate]):
            model = User

        service = UserService(db)
        user = await service.get_by_id(user_id)
    """

    model: type[ModelT]

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, id: uuid.UUID) -> ModelT:
        result = await self.db.execute(select(self.model).where(self.model.id == id))
        instance = result.scalar_one_or_none()
        if instance is None:
            raise NotFoundException(f"{self.model.__name__} not found")
        return instance

    async def get_all(
        self, *, page: int = 1, size: int = DEFAULT_PAGE_SIZE
    ) -> tuple[list[ModelT], int]:
        offset = (page - 1) * size
        items = await self.db.execute(select(self.model).offset(offset).limit(size))
        total = await self.db.execute(select(func.count()).select_from(self.model))
        return list(items.scalars().all()), total.scalar_one()

    async def create(self, instance: ModelT) -> ModelT:
        self.db.add(instance)
        await self.db.flush()
        return instance

    async def update(self, id: uuid.UUID, data: UpdateModelT) -> ModelT:
        instance = await self.get_by_id(id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(instance, field, value)
        await self.db.flush()
        return instance

    async def delete(self, id: uuid.UUID) -> None:
        instance = await self.get_by_id(id)
        await self.db.delete(instance)
        await self.db.flush()
