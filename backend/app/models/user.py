from backend.app.models.base import AppModel
from sqlalchemy import String, text
from sqlalchemy.orm import Mapped, mapped_column


class User(AppModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        default=True, server_default=text("true"), nullable=False
    )
