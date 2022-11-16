from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange

import psycopg2
import time
from psycopg2.extras import RealDictCursor


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

def find_post(id):
    for ele in my_posts:
        if ele["id"] == id:
            return ele
    return None

def find_index_post(id):
    for idx,ele in enumerate(my_posts):
        if ele["id"] == id:
            return idx
    return -1

@app.get("/")
def hello():
    return {"message" :"This is my first app"}

@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts  =  cursor.fetchall()
    return {"data":posts}

@app.post("/posts",status_code = status.HTTP_201_CREATED)
def create_posts(post : Post):
    post_dict = post.dict()
    post_dict["id"] = randrange(0,999999)
    my_posts.append(post_dict)
    return {"data" : post_dict}

@app.get("/posts/{post_id}")
def get_post(post_id : int, response : Response):
    post = find_post(int(post_id))
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id : {post_id} does not exist.")
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"message" : f"post with id : {post_id} does not exist."}
    print(post)

    return {"post detail ":post}

@app.delete("/posts/{post_id}",status_code = status.HTTP_204_NO_CONTENT)
def delete_post(post_id : int):
    idx = find_index_post(int(post_id))
    if idx == -1:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = f"The post with id : {post_id} does not exist")
    else:
        my_posts.pop(idx)

    return Response(status_code = status.HTTP_204_NO_CONTENT)


@app.put("/posts/{post_id}")
def update_post(post_id:int, post:Post):

    idx = find_index_post(int(post_id))
    if idx == -1:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = f"The post with id : {post_id} does not exist")
    post_dict = post.dict()
    post_dict["id"] = post_id
    my_posts[idx] = post_dict

    return {"message" : "New post successfully added",
            "data" : post_dict}