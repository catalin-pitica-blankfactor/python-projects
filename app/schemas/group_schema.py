from pydantic import BaseModel


class GroupCreate(BaseModel):
    name: str


class GroupResponseForCreate(BaseModel):
    uuid: str

    class Config:
        orm_mode = True


class GroupResponseForGet(BaseModel):
    uuid: str
    name: str

    class Config:
        orm_mode = True
