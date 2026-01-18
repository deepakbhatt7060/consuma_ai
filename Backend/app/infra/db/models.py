
#DB models

from sqlalchemy import Column, String, Integer, JSON, Float,  BigInteger
from app.infra.db.base import Base


class RequestDB(Base):
    __tablename__ = "requests"

    id = Column(String(255), primary_key=True)
    mode = Column(String(50))
    status = Column(String(50))

    payload = Column(JSON)
    result = Column(JSON, nullable=True)

    callback_attempts = Column(Integer, default=0)
    last_error = Column(String(255), nullable=True)

    started_at_ms = Column(BigInteger, nullable=True)
    completed_at_ms = Column(BigInteger, nullable=True)
    callback_completed_at_ms = Column(BigInteger, nullable=True)

    execution_time_ms = Column(Float, nullable=True)
    callback_time_ms = Column(Float, nullable=True)

