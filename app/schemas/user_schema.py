from pydantic import BaseModel


class UserCreate(BaseModel):
    user_name: str
    user_group: str


class UserUpdate(BaseModel):
    user_name: str
    group_name: str


class UserResponse(BaseModel):
    uuid: str

    class Config:
        from_attributes = True


class UserResponseForGet(BaseModel):
    uuid: str
    name: str
    group_name: list[str]
    url: dict

    class Config:
        from_attributes = True

