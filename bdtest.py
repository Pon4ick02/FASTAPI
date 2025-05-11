from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated, List
from pydantic import BaseModel, Field, constr

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import select

app = FastAPI(title="Books API", version="1.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


DATABASE_URL = "sqlite+aiosqlite:///books.db"
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]



class Base(DeclarativeBase):
    pass


class BookModel(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    author: Mapped[str]



class BookAddSchema(BaseModel):
    title: constr(min_length=1, max_length=100)
    author: constr(min_length=1, max_length=100)


class BookSchema(BookAddSchema):
    id: int

    class Config:
        orm_mode = True



@app.post('/setup-database')
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    return {"message": "Database setup complete"}


@app.post('/add-book', response_model=BookSchema)
async def add_book(data: BookAddSchema, session: SessionDep):
    new_book = BookModel(**data.dict())
    session.add(new_book)
    await session.commit()
    await session.refresh(new_book)
    return new_book


@app.get('/get-books', response_model=List[BookSchema])
async def get_books(session: SessionDep):
    result = await session.execute(select(BookModel))
    return result.scalars().all()


@app.get('/get-book/{book_id}', response_model=BookSchema)
async def get_book(book_id: int, session: SessionDep):
    result = await session.execute(select(BookModel).where(BookModel.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.put('/update-book/{book_id}', response_model=BookSchema)
async def update_book(book_id: int, data: BookAddSchema, session: SessionDep):
    result = await session.execute(select(BookModel).where(BookModel.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    book.title = data.title
    book.author = data.author
    await session.commit()
    await session.refresh(book)
    return book


@app.delete('/delete-book/{book_id}')
async def delete_book(book_id: int, session: SessionDep):
    result = await session.execute(select(BookModel).where(BookModel.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    await session.delete(book)
    await session.commit()
    return {"message": f"Book with id {book_id} deleted"}


@app.get('/search-books', response_model=List[BookSchema])
async def search_books(author: str = "", session: SessionDep = Depends(get_session)):
    query = select(BookModel)
    if author:
        query = query.where(BookModel.author.ilike(f"%{author}%"))
    result = await session.execute(query)
    return result.scalars().all()



if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
