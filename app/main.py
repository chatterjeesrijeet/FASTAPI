from fastapi import FastAPI

import time

import psycopg2
from psycopg2.extras import RealDictCursor

from .database import engine
from . import models
from .routers import post,user

models.Base.metadata.create_all(bind = engine)

app = FastAPI()

app.include_router(post.router)
app.include_router(user.router)


while True:
    try:
        conn = psycopg2.connect(
            host = "localhost",
            database = "fastapi",
            user = "postgres",
            password = "1234",
            cursor_factory = RealDictCursor
        )
        cursor = conn.cursor()
        print("Database connected successfully!!!")
        break

    except Exception as error:
        print("connection to database failed !!!")
        print("Error:",error)
        time.sleep(2)




@app.get("/")
def hello():
    return {"message" :"This is my first app"}
