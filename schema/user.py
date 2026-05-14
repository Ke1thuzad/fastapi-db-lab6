from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=128)
    last_name: str = Field(..., min_length=1, max_length=128)
    phone_number: str = Field(..., min_length=1, max_length=16)
    address: str = Field(..., min_length=1, max_length=512)


class UserSchema(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class UserCreateSchema(UserBase):
    pass