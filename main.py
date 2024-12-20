from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models import User,Post
from schemas import UserCreate, UserResponse
from crud import get_user, create_user, verify_password
from utils import create_access_token,verify_token
from datetime import timedelta
from schemas import UserCreate
from models import Post, User
from schemas import PostCreate, PostResponse

app = FastAPI()
Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@app.post("/users/", response_model=UserResponse)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return create_user(db, user)


@app.post("/login/")
def login_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user(db, user.username)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": db_user.username}, expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/", response_model=list[UserResponse])
def read_users(db: Session = Depends(get_db)):
    return db.query(User).all()
@app.get("/posts/", response_model=list[PostResponse])
def get_posts(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = verify_token(token, db)
    posts = db.query(Post).filter(Post.owner_id == user.id).all()
    return posts

@app.post("/posts/", response_model=PostResponse)
def create_post(post: PostCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = verify_token(token, db)
    db_post = Post(title=post.title, content=post.content, owner_id=user.id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post