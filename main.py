import bleach 
from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, field_validator
import re 

# [중요] 우리가 만든 파일들 불러오기
from routers import kiosk, booth
import models
from database import engine, get_db

# 1. 서버 시작할 때 DB 테이블 만들기
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# 라우터 연결
app.include_router(kiosk.router)
app.include_router(booth.router)

# 2. 설정 (보안 관련)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "my_super_secret_key_singpick"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 


# 3. 핵심 함수들
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 4. 데이터 모델 (입력받는 양식)
class UserCreate(BaseModel):
    user_id: str = Field(..., pattern=r"^[a-zA-Z]{4,20}$", description="4~20자 영문 전용")
    
    phone: str = Field(..., pattern=r"^010\d{8}$", description="010XXXXXXXX")
    
    password: str = Field(..., pattern=r"^\d{1,6}$", description="숫자 1~6자리")

    @field_validator('user_id')
    def validate_user_id(cls, v):
        if not v.isalpha(): 
            raise ValueError('아이디는 숫자가 포함될 수 없으며, 오직 영문만 가능합니다.')
        return v
    
class UserLogin(BaseModel):
    phone: str
    password: str


# 5. API
@app.get("/")
def read_root():
    return {"status": "success", "message": "SingPick Server Running with MySQL"}

# [회원가입 API]
@app.post("/signup", tags=["Auth (회원가입/로그인)"])
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # 1. 이미 가입된 번호인지 DB에서 조회 (SQL: SELECT * FROM users WHERE phone = ...)
    db_user = db.query(models.User).filter(models.User.phone == user.phone).first()
    
    if db_user:
        raise HTTPException(status_code=400, detail="이미 가입된 전화번호입니다.")
    
    # 2. 비밀번호 암호화 및 저장
    hashed_password = get_password_hash(user.password)
    
    # 3. DB 모델(설계도)에 데이터 채우기
    new_user = models.User(
        user_id=user.user_id,
        phone=user.phone,
        password=hashed_password
    )
    
    # 4. 진짜 저장 (Commit)
    db.add(new_user)
    db.commit()
    
    return {
        "status": "success", 
        "message": f"Welcome {user.user_id}! Signup Complete.",
        "user_phone": user.phone
    }

# [로그인 API]
@app.post("/login", tags=["Auth (회원가입/로그인)"])
def login(user: UserLogin, db: Session = Depends(get_db)):
    # 1. DB에서 전화번호로 찾기
    db_user = db.query(models.User).filter(models.User.phone == user.phone).first()
    
    if not db_user:
        raise HTTPException(status_code=400, detail="User not found.")
    
    # 2. 비밀번호 확인 (DB에 있는 암호화된 비번과 비교)
    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Incorrect password.")
    
    # 3. 토큰 발급
    access_token = create_access_token(data={"sub": user.phone})
    
    return {
        "status": "success",
        "data": {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": db_user.user_id
        }
    }