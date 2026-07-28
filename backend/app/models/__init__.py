"""Model registry for Alembic autogenerate.

Every model must be imported here so it registers on ``Base.metadata`` before
Alembic inspects it. Import your models below, e.g.::

    from backend.app.models.user import User  # noqa: F401

``alembic/env.py`` imports this package, so anything listed here is picked up by
``alembic revision --autogenerate``.
"""

from backend.app.models.base import AppModel, Base
from backend.app.models.user import User

__all__ = ["AppModel", "Base", "User"]
