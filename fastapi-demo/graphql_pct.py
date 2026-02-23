from fastapi import FastAPI
import strawberry
from strawberry.fastapi import GraphQLRouter


@strawberry.type
class Book:
    title: str
    author: str
    price: int

@strawberry.type
class Query:
    @strawberry.field
    def book(self) -> Book:
        return Book(title="Computer Fundmentals", author="Ayushi", price=320)
    
schema = strawberry.Schema(query = Query)

graphql_app = GraphQLRouter(schema)
app = FastAPI()

app.include_router(graphql_app, prefix="/book")


