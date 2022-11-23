from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body

from typing import Optional, List
from random import randrange

import time

import psycopg2
from psycopg2.extras import RealDictCursor

from sqlalchemy.orm import Session

from .database import engine, get_db
from . import models, schemas, utils

models.Base.metadata.create_all(bind = engine)

app = FastAPI()


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


@app.get("/posts", response_model=List[schemas.Post])
def get_posts(db : Session = Depends(get_db)):

    # cursor.execute("""SELECT * FROM posts""")
    # posts  =  cursor.fetchall()

    posts = db.query(models.Post).all()
    return posts


@app.post("/posts", status_code = status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post : schemas.PostCreate, db : Session = Depends(get_db)):

    # cursor.execute( """ INSERT INTO posts (title,content,published) VALUES (%s,%s,%s) RETURNING * """,
    #                 (post.title,post.content,post.published)
    #                )
    # new_post = cursor.fetchone()
    # conn.commit()

    # new_post = models.Post(
    #     title = post.title, content = post.content, published = post.published)

    new_post = models.Post(
        **post.dict())

    # print(post.dict())

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

@app.get("/posts/{id}", response_model=schemas.Post)
def get_post(id : int,db : Session = Depends(get_db)):

    # cursor.execute( """ SELECT * FROM posts WHERE id = %s """,
    #                 (str(id)) )
    # post = cursor.fetchone()

    post = db.query(models.Post).filter(models.Post.id == id).first()
    print(post)

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail = f"post with id : {id} does not exist.")
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"message" : f"post with id : {post_id} does not exist."}
    return post


@app.delete("/posts/{id}",status_code = status.HTTP_204_NO_CONTENT)
def delete_post(id : int, db : Session = Depends(get_db)):

    # cursor.execute("""DELETE FROM posts WHERE id = %s returning *""", (str(id)))
    # deleted_post = cursor.fetchone()
    # conn.commit()

    deleted_post = db.query(models.Post).filter(models.Post.id ==id)

    if deleted_post.first() == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = f"The post with id : {id} does not exist")
    deleted_post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code = status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}", response_model=schemas.Post)
def update_post(id:int, post:schemas.PostBase,  db : Session = Depends(get_db)):

    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published=%s WHERE id = %s RETURNING *""",
    #                 (post.title, post.content, post.published, str(id)))
    # post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)
    updated_post = post_query.first()

    if updated_post == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = f"The post with id : {id} does not exist")
    
    post_query.update(post.dict(), 
                        synchronize_session=False)
    db.commit()

    return post_query.first()


@app.post("/users", status_code = status.HTTP_201_CREATED, response_model= schemas.UserOut)
def register_user(user : schemas.UserCreate, db : Session = Depends(get_db)):

    new_user = models.User(**user.dict())

    hashed_password = utils.hash(new_user.password)
    new_user.password = hashed_password

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

    

