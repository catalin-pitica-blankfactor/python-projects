from pydantic import BaseModel


class GroupCreate(BaseModel):
    name: str


class GroupResponseForCreate(BaseModel):
    uuid: str

    class Config:
        from_attributes = True


class GroupResponseForGet(BaseModel):
    uuid: str
    name: str

    class Config:
        from_attributes = True
