from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Annotated

import models
from database import engine, SessionLocal

class BookBase(BaseModel):
    title: str
    author: str
    year: int

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/")
async def root():
    return {"message": "Gestor de libros"}

@app.get("/books")
async def get_books(db: db_dependency):
    return db.query(models.Book).all()

@app.get("/books/{book_id}")
async def get_book(book_id: int, db: db_dependency):
    return db.query(models.Book).filter(models.Book.id == book_id).first()

@app.post("/books", response_model=BookBase)
async def create_book(book: BookBase, db: db_dependency):
    db_book = models.Book(**book.dict())
    db.add(db_book)
    db.commit()
    return db_book

@app.delete("/books/{book_id}")
async def delete_book(book_id: int, db: db_dependency):
    db.query(models.Book).filter(models.Book.id == book_id).delete()
    db.commit()
    return {"message": "Book deleted"}

@app.put("/books/{book_id}", response_model=BookBase)
async def update_book(book_id: int, book: BookBase, db: db_dependency):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    db_book.title = book.title
    db_book.author = book.author
    db_book.year = book.year
    db.commit()
    return db_book