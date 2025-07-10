from pydantic import BaseModel
from typing import List, Optional


class RouteBase(BaseModel):
    path: str
    label: str
    icon: Optional[str] = None
    is_active: bool = True
    is_sidebar: bool = True
    module_id: int
    parent_id: Optional[int] = None


class RouteCreate(RouteBase):
    role_ids: Optional[List[int]] = []


class RouteUpdate(BaseModel):
    path: Optional[str] = None
    is_active: Optional[bool] = None
    label: Optional[str] = None
    is_sidebar: bool = True
    module_id: Optional[int] = None
    parent_id: Optional[int] = None
    role_ids: Optional[List[int]] = []
    icon: Optional[str] = None


class RouteResponse(RouteBase):
    id: int
    role_ids: List[int] = []

    class Config:
        from_attributes = True
