from typing import Generic, TypeVar, List

from pydantic import BaseModel, ConfigDict

T = TypeVar('T')

class ResponseWrapper(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int

    model_config = ConfigDict(from_attributes=True)