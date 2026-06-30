from pydantic import BaseModel, ConfigDict


class AppSchema(BaseModel):
    """
    Base class for all Pydantic schemas in this project.

    - from_attributes: allows building a schema directly from an ORM model instance
    - populate_by_name: accepts both field name and alias when parsing input
    - use_enum_values: serializes enums to their raw value automatically
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True,
    )
