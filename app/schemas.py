from pydantic import BaseModel 
from fastapi import FastAPI, Query
from typing import Union

class BookCreate(BaseModel):
    name: str
    author: str = Query(min_length=3, max_length=30,)
    count_page: int = Query(ge = 10)

class Book(BookCreate):
    id: int
    class Config():
        from_attributes = True
    
class UserGet(BaseModel):
    id: int
    username: str

class UserCreate(BaseModel):
    username: str
    password: str
    
class User(UserCreate):
    id: int
    class Config():
        from_attributes = True

