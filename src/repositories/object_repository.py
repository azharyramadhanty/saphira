from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from src.models.object import Object
from sqlalchemy import func
from src.utils.db_utils import prevent_sql_injection_safe


class ObjectRepository:
    """
    Repository for accessing Object data from the database asynchronously.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_by_question(
        self, client_id: str, question: str
    ) -> list[Object]:
        question_safe = prevent_sql_injection_safe(question)
        ts_query_str = question_safe.replace(" ", "|")

        query = (
            select(
                Object.client_id,
                Object.object_id,
                Object.object_tag
            )
            .select_from(Object)
            .where(Object.client_id == client_id)
            .where(
                Object.object_token.op(
                    "@@")(func.to_tsquery("english", ts_query_str))
            )
        )

        result = await self.session.exec(query)
        return result.all()
