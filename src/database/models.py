from sqlalchemy import CheckConstraint, Enum, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, validates

from .utils import DifficultyEnum


class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nickname: Mapped[str] = mapped_column(String(5), nullable=False)
    artist: Mapped[str] = mapped_column(String)
    difficulty: Mapped[DifficultyEnum] = mapped_column(
        Enum(DifficultyEnum, name="difficulty_enum"),
        default=DifficultyEnum.Unknown,
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    version_id: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __table_args__ = (
        Index("ix_users_score", "score"),
        UniqueConstraint(
            "nickname", "artist", "difficulty", name="uq_users_nickname_artist"
        ),
        CheckConstraint("LENGTH(nickname) <= 5", name="ck_nickname_length"),
    )
    __mapper_args__ = {"version_id_col": version_id}


    @validates("nickname")
    def validate_nickname(self, key: str, value: str):
        """Валидация поля nickname

        :param key: название поля для валидации в данном случае - nickname
        :type key: str
        :param value: Значение для валидации
        :type value: str
        :raises ValueError: Превышение ограничения символов
        :return: ValueError
        :rtype: str
        """        
        if len(value) > 5:
            raise ValueError("Nickname must be 5 characters or fewer")
        return value

    @validates("difficulty")
    def validate_status(self, key: str, value: str):
        """Валидация поля difficulty

        :param key: название поля для валидации в данном случае - difficulty
        :type key: str
        :param value: Значение для валидации
        :type value: str
        :return: Значение сложности
        :rtype: str
        """        
        allowed_statuses = DifficultyEnum.get_values()
        if value not in allowed_statuses:
            value = DifficultyEnum.Unknown.value
        return value
