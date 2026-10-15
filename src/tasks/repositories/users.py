from pydantic import EmailStr
from sqlalchemy import select

from src.models.users import UsersOrm
from tasks.repositories.base import BaseRepository
from tasks.repositories.mappers.mappers import UserDataMapper
from src.schemas.users import UserWithHashPass


class UsersRepository(BaseRepository):
    model = UsersOrm
    mapper = UserDataMapper

    async def get_user_with_hashed_pass(self, email: EmailStr) -> UserWithHashPass:
        query = select(self.model).filter_by(email=email)
        result = await self.session.execute(query)
        user = result.scalars().one()

        return self.mapper.map_to_domain_entity(user)
