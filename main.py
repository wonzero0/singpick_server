import bleach 
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, field_validator
import re 
import bleach
from routers import kiosk, booth
import models
from database import engine, get_db
from utils import aes_encrypt, aes_decrypt

# 1. 서버 시작할 때 DB 테이블 만들기
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

#CORS 설정 
origins = [
    "http://localhost:3000", # 리액트(React) 등 프론트엔드 주소
    "*"                      # (테스트용) 모든 주소 허용
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # 허용할 주소 목록
    allow_credentials=True,     # 자격 증명(쿠키 등) 허용 여부
    allow_methods=["*"],        # 허용할 HTTP 메서드 (GET, POST 등 전체)
    allow_headers=["*"],        # 허용할 헤더 (전체)
)

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

# 4. 데이터 모델 
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
    # ▼ [추가] 전화번호 암호화 (01012345678 -> gRgx/...)
    crypto_phone = aes_encrypt(user.phone)

    # 1. 이미 가입된 번호인지 조회 (암호화된 값으로 비교해야 함!)
    db_user = db.query(models.User).filter(models.User.phone == crypto_phone).first()
    
    if db_user:
        raise HTTPException(status_code=400, detail="이미 가입된 전화번호입니다.")
    
    # XSS 방어 (기존 코드)
    clean_user_id = bleach.clean(user.user_id)
    
    # 비밀번호 해시 (기존 코드)
    hashed_password = get_password_hash(user.password)
    
    # 2. DB 저장 (전화번호는 암호화된 상태로)
    new_user = models.User(
        user_id=clean_user_id,
        phone=crypto_phone,  # [변경] user.phone -> crypto_phone
        password=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    
    return {"status": "success", "message": f"Welcome {clean_user_id}! Signup Complete."}

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