from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange

import time

import psycopg2
from psycopg2.extras import RealDictCursor

from sqlalchemy.orm import Session
from . import models
from .database import engine, SessionLocal, get_db

models.Base.metadata.create_all(bind = engine)


app = FastAPI()

class Post(BaseModel):
    title : str
    content : str
    published : bool = True
    rating : Optional[int] = None

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


@app.get("/sqlalchemy")
def test_posts(db : Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"data" : posts}


@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts  =  cursor.fetchall()
    return {"data":posts}


@app.post("/posts",status_code = status.HTTP_201_CREATED)
def create_posts(post : Post):
    cursor.execute( """ INSERT INTO posts (title,content,published) VALUES (%s,%s,%s) RETURNING * """,
                    (post.title,post.content,post.published)
                   )
    new_post = cursor.fetchone()
    conn.commit()
    return {"data" : new_post }


@app.get("/posts/{id}")
def get_post(id : int, response : Response):

    cursor.execute( """ SELECT * FROM posts WHERE id = %s """,
                    (str(id)) )
    post = cursor.fetchone()
    print(post)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail = f"post with id : {id} does not exist.")
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"message" : f"post with id : {post_id} does not exist."}
    return {"post detail ": post}


@app.delete("/posts/{id}",status_code = status.HTTP_204_NO_CONTENT)
def delete_post(id : int):
    cursor.execute("""DELETE FROM posts WHERE id = %s returning *""", (str(id)))
    deleted_post = cursor.fetchone()
    conn.commit()

    if deleted_post == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = f"The post with id : {id} does not exist")

    return Response(status_code = status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id:int, post:Post):
    cursor.execute("""UPDATE posts SET title = %s, content = %s, published=%s WHERE id = %s RETURNING *""",
                    (post.title, post.content, post.published, str(id)))
    updated_post = cursor.fetchone()
    conn.commit()
    
    if updated_post == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = f"The post with id : {id} does not exist")
    
    return {"message" : "New post successfully added",
            "data" : updated_post}

