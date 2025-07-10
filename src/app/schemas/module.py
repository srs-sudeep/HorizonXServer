from pydantic import BaseModel
from typing import Optional


class ModuleBase(BaseModel):
    name: str
    label: str
    icon: Optional[str] = None
    is_active: bool = True


class ModuleCreate(ModuleBase):
    pass


class ModuleUpdate(BaseModel):
    name: Optional[str] = None
    label: Optional[str] = None
    icon: Optional[str] = None
    is_active: Optional[bool] = None


class ModuleResponse(ModuleBase):
    id: int

    class Config:
        from_attributes = True
