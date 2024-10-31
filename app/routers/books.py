from fastapi import Depends, HTTPException , APIRouter ,Form 
from fastapi.responses import RedirectResponse
from app.schemas import BookCreate ,Book, UserCreate,User , UserGet
from starlette.requests import Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db.crud import create_book_db , get_book_db , get_books_db, create_user_db,edit_book_db,pwd_context, token_create , get_user , delete_book_db
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
def main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/token")
def token_get(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],db: Session = Depends(get_db)):
    user_data = get_user(db,form_data.username)
    if not user_data:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    else:
        global user
        user = user_data
        if not pwd_context.verify(form_data.password, user.password):
            raise HTTPException(status_code=400, detail="Incorrect username or password")
        token = token_create(data={"sub": user.username})

    return {"access_token": token, "token_type": "bearer"}

@router.post("/sign-up-user", response_model=UserCreate)
def create_user(user:Annotated[UserCreate, Form()] , db: Session = Depends(get_db)):
    create_user_db(db=db, user=user)
    return RedirectResponse(url="/books", status_code=303)

@router.get("/sign-up")
def sign_up(request :Request):
    return templates.TemplateResponse("sign_up.html", {"request": request})

@router.post("/books/addNew")
def create_book(book_form: Annotated[BookCreate, Form()] , db: Session = Depends(get_db)):
    create_book_db(db=db, book=book_form)
    return RedirectResponse(url="/books", status_code=303)

@router.get("/books/addNew")
def creating_book(request: Request):
    return templates.TemplateResponse("add_book.html", {"request": request})

@router.get("/books", response_model=list[Book])
def get_books(request: Request,skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    books = get_books_db(db, skip=skip, limit=limit)
    return templates.TemplateResponse("all_books.html", {"request": request, "books": books})

@router.get("/books/{book_id}", response_model=Book)
def get_book(request: Request,book_id: int, db: Session = Depends(get_db)):
    book = get_book_db(db, book_id=book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return templates.TemplateResponse("book.html", {"request": request, "book": book})
    
@router.post("/books/{book_id}")
def delete_book(book_id: int,db: Session = Depends(get_db)):
    delete_book_db(db=db,book_id=book_id)
    return RedirectResponse(url="/books", status_code=303)

@router.get("/books/{book_id}/edit")
def edit_book(request: Request, book_id: int, db: Session = Depends(get_db)):
    db_book = get_book_db(db, book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    
    return templates.TemplateResponse("edit_book.html", {"request": request, "book": db_book})

@router.post("/book/{book_id}", response_model=Book)
def edit(book_id: int,name: str = Form(...),author: str = Form(...),count_page: int = Form(...),db: Session = Depends(get_db)):
    book_data = BookCreate(name=name, author=author, count_page=count_page)
    edit_book_db(db=db, book_data=book_data, book_id=book_id)
    return RedirectResponse(url="/books", status_code=303)
