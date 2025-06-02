from sqlmodel import SQLModel
from sqlalchemy.orm import declared_attr
from src.utils.db_utils import to_snake_case


class Base(SQLModel):
    __name__: str

    # Generate table name automatically
    @declared_attr
    def __tablename__(cls) -> str:  # pylint: disable=no-self-argument
        return to_snake_case(cls.__name__)
