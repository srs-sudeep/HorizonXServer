from pydantic import BaseModel
from typing import List, Optional, Dict


class SidebarComponentItem(BaseModel):
    component_id: str


class SidebarRouteItem(BaseModel):
    id: int
    label: str
    path: Optional[str] = None
    icon: Optional[str] = None
    isActive: bool
    is_sidebar: bool
    parent_id: Optional[int] = None
    module_id: Optional[int] = None
    children: List["SidebarRouteItem"] = []
    roles: List[Dict[str, str]] = []
    components: List[SidebarComponentItem] = []

    class Config:
        from_attributes = True


SidebarRouteItem.model_rebuild()


class SidebarModuleItem(BaseModel):
    id: int
    label: str
    icon: Optional[str] = None
    isActive: bool
    subModules: List[SidebarRouteItem] = []

    class Config:
        from_attributes = True
