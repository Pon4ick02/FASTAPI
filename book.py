from fastapi import FastAPI, File, UploadFile
import uvicorn
from pydantic import BaseModel
app = FastAPI()


books = [
    {
        "id": 1,
        "title": "Book 1",
        "author": "Author 1"
    },
    {
        "id": 2,
        "title": "Book 2",
        "author": "Author 2"
    }
]


class BookSchema(BaseModel):
    title: str
    author: str



@app.get('/all_books/', tags=["books"], description="Get all books", summary="Get all books")
async def get_all_books():
    return books




@app.get('/book/{book_id}', tags=["books"], description="Get a book by id", summary="Get a book by id")
async def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book
    return {"message": "Book not found"}


@app.post('/create_book', tags=["books"], description="Create a book", summary="Create a book")
async def create_book(book: BookSchema):
    new_book = {"id": len(books) + 1, **book.model_dump()}
    books.append(new_book)
    return new_book


@app.put('/update_book/{book_id}', tags=["books"], description="Update a book", summary="Update a book")
async def update_book(book_id: int, book: BookSchema):
    books[book_id] = book
    return books[book_id]


@app.delete('/delete_book/{book_id}', tags=["books"], description="Delete a book", summary="Delete a book")
async def delete_book(book_id: int):
    books.pop(book_id)
    return books





if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)









