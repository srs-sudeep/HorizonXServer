from sqlalchemy import Column, Integer, String, Boolean
from src.core.db import Base


class Module(Base):
    __tablename__ = "module"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False, index=True)
    label = Column(String, nullable=False)
    icon = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
