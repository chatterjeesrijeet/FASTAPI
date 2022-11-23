
from fastapi import FastAPI, status, HTTPException, Depends


from ..database import get_db
from .. import models, schemas, utils

from sqlalchemy.orm import Session


@app.post("/users", status_code = status.HTTP_201_CREATED, response_model= schemas.UserOut)
def register_user(user : schemas.UserCreate, db : Session = Depends(get_db)):

    new_user = models.User(**user.dict())

    hashed_password = utils.hash(new_user.password)
    new_user.password = hashed_password

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.get("/users/{id}", response_model= schemas.UserOut)
def get_user(id : int, db : Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, 
                            detail = f"User with {id} does not exist")
    return user    
