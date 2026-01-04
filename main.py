from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

app = FastAPI()

# ==========================================
# 1. 설정 (보안 관련)
# ==========================================
# 비밀번호 암호화 도구
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 토큰 설정 (임시 비밀키, 실무에선 절대 이렇게 공개하면 안 됨!)
SECRET_KEY = "my_super_secret_key_singpick"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 토큰 유효시간 30분

# ==========================================
# 2. 핵심 함수들 (암호화, 토큰 생성)
# ==========================================
# (1) 비밀번호 검증 함수: 사용자가 입력한 비번 vs DB에 저장된 암호화 비번 비교
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# (2) 비밀번호 암호화 함수
def get_password_hash(password):
    return pwd_context.hash(password)

# (3) JWT 토큰 생성 함수 (자유이용권 발급기)
def create_access_token(data: dict):
    to_encode = data.copy()
    # 유효기간 설정 (현재시간 + 30분)
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # 토큰 암호화해서 생성
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ==========================================
# 3. 데이터 모델 (주문서 양식)
# ==========================================
class UserCreate(BaseModel):
    email: str
    password: str

# 가짜 DB (아직 진짜 DB가 없으니 리스트에 저장)
fake_users_db = {}

# ==========================================
# 4. API (기능)
# ==========================================

@app.get("/")
def read_root():
    return {"status": "success", "message": "Hello World"}

# 회원가입 (비밀번호 암호화해서 저장)
@app.post("/signup")
def signup(user: UserCreate):
    # 이미 있는 이메일인지 확인
    if user.email in fake_users_db:
        raise HTTPException(status_code=400, detail="이미 가입된 이메일입니다.")
    
    hashed_password = get_password_hash(user.password)
    # 가짜 DB에 저장
    fake_users_db[user.email] = {
        "email": user.email,
        "password": hashed_password
    }
    
    return {"status": "success", "message": "회원가입 완료", "user": user.email}

# [cite_start]로그인 (아이디/비번 확인 후 토큰 발급) [cite: 10]
@app.post("/login")
def login(user: UserCreate):
    # 1. 이메일이 있는지 확인
    db_user = fake_users_db.get(user.email)
    if not db_user:
        raise HTTPException(status_code=400, detail="이메일 또는 비밀번호가 틀렸습니다.")
    
    # 2. 비밀번호가 맞는지 확인
    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="이메일 또는 비밀번호가 틀렸습니다.")
    
    # 3. 다 맞으면 토큰 발급
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "status": "success",
        "data": {
            "access_token": access_token,
            "token_type": "bearer"
        }
    }