
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from typing import List

from ..database import get_db
from .. import models, schemas, utils

from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/posts", response_model=List[schemas.Post])
def get_posts(db : Session = Depends(get_db)):

    # cursor.execute("""SELECT * FROM posts""")
    # posts  =  cursor.fetchall()

    posts = db.query(models.Post).all()
    return posts


@router.post("/posts", status_code = status.HTTP_201_CREATED, response_model=schemas.Post)
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

@router.get("/posts/{id}", response_model=schemas.Post)
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


@router.delete("/posts/{id}",status_code = status.HTTP_204_NO_CONTENT)
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


@router.put("/posts/{id}", response_model=schemas.Post)
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
