from datetime import UTC, datetime

from sqlalchemy import BigInteger, ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from bot.internal.enums import Nomination


class Base(DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC), server_default=func.now())


class User(Base):
    __tablename__ = 'users'

    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    fullname: Mapped[str]
    username: Mapped[str | None] = mapped_column(String(32))
    phone_number: Mapped[str | None] = mapped_column(String(20))
    voted_1: Mapped[bool] = mapped_column(default=False)
    voted_2: Mapped[bool] = mapped_column(default=False)
    voted_3: Mapped[bool] = mapped_column(default=False)
    voted_4: Mapped[bool] = mapped_column(default=False)
    voted_5: Mapped[bool] = mapped_column(default=False)
    voted_6: Mapped[bool] = mapped_column(default=False)
    voted_7: Mapped[bool] = mapped_column(default=False)
    voted_8: Mapped[bool] = mapped_column(default=False)
    voted_9: Mapped[bool] = mapped_column(default=False)
    voted_10: Mapped[bool] = mapped_column(default=False)
    voted_11: Mapped[bool] = mapped_column(default=False)
    voted_12: Mapped[bool] = mapped_column(default=False)
    voted_13: Mapped[bool] = mapped_column(default=False)

    def __str__(self) -> str:
        return f'User(id={self.id}, fullname={self.fullname}, telegram_id={self.telegram_id})'

    def __repr__(self) -> str:
        return self.__str__()


class Nominee(Base):
    __tablename__ = 'nominees'

    name: Mapped[str]
    last_name: Mapped[str | None]
    link: Mapped[str]
    nomination: Mapped[Nomination] = mapped_column(index=True)


class Vote(Base):
    __tablename__ = 'votes'
    __table_args__ = (
        UniqueConstraint('user_id', 'nomination', name='uq_votes_user_nomination'),
        Index('ix_votes_nomination', 'nomination'),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)
    nomination: Mapped[Nomination]
    vote_for_1: Mapped[int] = mapped_column(ForeignKey('nominees.id', ondelete='CASCADE'))
    vote_for_2: Mapped[int] = mapped_column(ForeignKey('nominees.id', ondelete='CASCADE'))
    vote_for_3: Mapped[int] = mapped_column(ForeignKey('nominees.id', ondelete='CASCADE'))
