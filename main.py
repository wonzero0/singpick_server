from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

from routers import kiosk, booth


app = FastAPI()

app.include_router(kiosk.router)  # 외부 키오스크 연결
app.include_router(booth.router)  # 내부 부스 연결

# ==========================================
# 1. 설정 (보안 관련)
# ==========================================
# 비밀번호 암호화 도구
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 토큰 설정
SECRET_KEY = "my_super_secret_key_singpick"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 

# ==========================================
# 2. 핵심 함수들 (암호화, 토큰 생성)
# ==========================================
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

# ==========================================
# 3. 데이터 모델 (설계서 반영!)
# ==========================================

class UserCreate(BaseModel):
    name: str           # 사용자 이름 (예: 홍길동)
    phone: str          # 전화번호 (예: 01012345678) - 이게 아이디 역할
    password: str       # 비밀번호 (숫자 6자리)

class UserLogin(BaseModel):
    phone: str          # 로그인할 때도 전화번호 사용
    password: str

# 가짜 DB (메모리에 임시 저장)
fake_users_db = {}

# ==========================================
# 4. API (키오스크에서 이 주소로 데이터를 보냄)
# ==========================================

@app.get("/")
def read_root():
    return {"status": "success", "message": "Hello world"}

# [회원가입 API]
@app.post("/signup", tags=["Auth (회원가입/로그인)"])
def signup(user: UserCreate):
    # 1. 이미 가입된 번호인지 확인
    if user.phone in fake_users_db:
        raise HTTPException(status_code=400, detail="이미 가입된 전화번호입니다.")
    
    # 2. 비밀번호 암호화
    hashed_password = get_password_hash(user.password)
    
    # 3. DB에 저장
    fake_users_db[user.phone] = {
        "name": user.name,
        "phone": user.phone,
        "password": hashed_password
    }
    
    return {
        "status": "success", 
        "message": f"{user.name}님 회원가입 완료! (키오스크 가입)", 
        "user_phone": user.phone
    }

# [로그인 API] - 키오스크에서 '회원' 버튼 누르고 입력했을 때
@app.post("/login", tags=["Auth (회원가입/로그인)"])
def login(user: UserLogin):
    # 1. 아이디(전화번호)가 있는지 확인
    db_user = fake_users_db.get(user.phone)
    if not db_user:
        raise HTTPException(status_code=400, detail="가입되지 않은 전화번호입니다.")
    
    # 2. 비밀번호가 맞는지 확인
    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="비밀번호가 틀렸습니다.")
    
    # 3. 입장권(토큰) 발급
    access_token = create_access_token(data={"sub": user.phone})
    
    return {
        "status": "success",
        "data": {
            "access_token": access_token,
            "token_type": "bearer",
            "user_name": db_user["name"] 
        }
    }