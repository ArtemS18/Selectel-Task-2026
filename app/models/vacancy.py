from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Vacancy(Base):
    __tablename__ = "vacancies"
    __table_args__ = (
        UniqueConstraint("external_id", name="uq_vacancies_external_id"),
        Index(
            "idx_vacancies_timetable_mode_name_trgm",
            "timetable_mode_name",
            postgresql_using="gin",
            postgresql_ops={"timetable_mode_name": "gin_trgm_ops"}
        ), # для ускорения поиска по timetable_mode_name
        Index(
            "idx_city_name_trgm",
            "city_name",
            postgresql_using="gin",
            postgresql_ops={"city_name": "gin_trgm_ops"}
        ), # для ускорения поиска по city_name
        )
    

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    timetable_mode_name: Mapped[str] = mapped_column(String, nullable=False)
    tag_name: Mapped[str] = mapped_column(String, nullable=False)
    city_name: Mapped[str | None] = mapped_column(String, nullable=True)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_remote_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_hot: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    external_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
