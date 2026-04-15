from sqlalchemy import Enum, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, validates

from .utils import DifficultyEnum


class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nickname: Mapped[str] = mapped_column(String(5), nullable=False)
    artist: Mapped[str] = mapped_column(String(50))
    difficulty: Mapped[DifficultyEnum] = mapped_column(
        Enum(DifficultyEnum, name="difficulty_enum"),
        default=DifficultyEnum.Unknown,
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    version_id: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __table_args__ = (
        Index("ix_users_score", "score"),
        UniqueConstraint("nickname", "artist", "difficulty", name="uq_users_nickname_artist"),
    )
    __mapper_args__ = {"version_id_col": version_id}

    @validates("difficulty")
    def validate_status(self, key: str, value: str):
        allowed_statuses = DifficultyEnum.get_values()
        if value not in allowed_statuses:
            value = DifficultyEnum.Unknown.value
        return value
