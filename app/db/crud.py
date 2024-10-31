from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError , jwt
from . import models
from app import schemas
import secrets
from app.schemas import UserCreate
from datetime import datetime , timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "19109197bd5e7c289b92b2b355083ea26c71dee2085ceccc19308a7291b2ea06"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def token_create(data: dict):
   expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
   to_encode = data.copy()
   if expires_delta:
      expire = datetime.utcnow() + expires_delta
   else:
      expire = datetime.utcnow() + timedelta(minutes=15)
   to_encode.update({"exp": expire})
   encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
   return encoded_jwt

def create_book_db(db: Session, book: schemas.BookCreate):
   db_book = models.Book(name=book.name,author=book.author,count_page=book.count_page)
   db.add(db_book)
   db.commit()
   db.refresh(db_book)

   return db_book

def create_user_db(db: Session, user: UserCreate): 
   hashed_password = get_password_hash(user.password )
   db_user = models.User(username=user.username, password=hashed_password)
   db.add(db_user)
   db.commit()
   db.refresh(db_user)
   return db_user

def get_user(db: Session, username: str):
   return db.query(models.User).filter(models.User.username == username).first()

def verify_password(plain_password, hashed_password, salt):
   return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
   return pwd_context.hash(password)

def get_book_db(db: Session, book_id: int):
   return db.query(models.Book).filter(models.Book.id == book_id).first()

def get_books_db(db: Session, skip: int = 0, limit: int = 100):
   return db.query(models.Book).offset(skip).limit(limit).all()

def delete_book_db(db: Session, book_id: int):
   db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
   
   if db_book:
      db.delete(db_book)
      db.commit()
   
   return db_book

def edit_book_db(db: Session, book_data: models.Book, book_id: int): #editing
   book = get_book_db(db, book_id)
   book.name = book_data.name
   book.author = book_data.author
   book.count_page = book_data.count_page
   db.commit()
   db.refresh(book)
   return book
