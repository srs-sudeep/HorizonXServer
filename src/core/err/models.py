"""Error models."""

from typing import Any, Dict, List, Union

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Error response model."""

    detail: Union[str, List[Dict[str, Any]]]
    status_code: int
