from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True

class PostCreate(BaseModel):
    title: str
    content: str

class PostResponse(PostCreate):
    id: int
    owner_id: int

    class Config:
        orm_mode = True