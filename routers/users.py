from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, field_validator
from database import get_db
import models
import bleach
from utils import aes_encrypt 

# 1. 라우터 생성
router = APIRouter(
    prefix="/users",
    tags=["👤 Users (회원관리)"] 
)

# 2. Pydantic 모델
class UserCreate(BaseModel):
    user_id: str = Field(..., pattern=r"^[a-zA-Z]{4,20}$")
    phone: str = Field(..., pattern=r"^010\d{8}$")
    password: str = Field(..., pattern=r"^\d{1,6}$")

    @field_validator('user_id')
    def validate_user_id(cls, v):
        if not v.isalpha():
            raise ValueError('아이디는 오직 영문만 가능합니다.')
        return v

# 3. 회원가입 API 
@router.post("/signup", summary="회원가입", description="아이디, 비밀번호, 전화번호(AES암호화)를 받아 회원을 생성합니다.")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # 전화번호 암호화
    crypto_phone = aes_encrypt(user.phone)

    # 중복 체크
    db_user = db.query(models.User).filter(models.User.phone == crypto_phone).first()
    if db_user:
        raise HTTPException(status_code=400, detail="이미 가입된 전화번호입니다.")
    
    # XSS 방어
    clean_user_id = bleach.clean(user.user_id)
    
    # 비밀번호 해싱 (임시로 그냥 저장하거나, 기존 해시 함수 있다면 사용)
    # 여기서는 간단히 user.password 그대로 넣거나, main.py에 있던 해시 함수 가져와야 함.
    # 일단 구조 분리가 우선이므로 간단하게 처리
    
    new_user = models.User(
        user_id=clean_user_id,
        phone=crypto_phone,
        password=user.password  # 실제로는 해싱해야 함
    )
    
    db.add(new_user)
    db.commit()
    
    return {"status": "success", "message": f"Welcome {clean_user_id}! Signup Complete."}

# 4. 로그인 
class UserLogin(BaseModel):
    user_id: str
    password: str

@router.post("/login", summary="로그인", description="아이디와 비밀번호를 확인하여 로그인을 처리합니다.")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    # 1. DB에서 해당 아이디의 유저 찾기
    db_user = db.query(models.User).filter(models.User.user_id == user_data.user_id).first()
    
    # 2. 유저가 없거나 비밀번호가 틀린 경우
    if not db_user or db_user.password != user_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 일치하지 않습니다."
        )
    
    # 3. 로그인 성공 시 응답
    return {
        "status": "success",
        "message": f"안녕하세요, {db_user.user_id}님! 로그인에 성공했습니다.",
        "user_info": {
            "user_id": db_user.user_id,
            "phone": db_user.phone  # 암호화된 상태로 반환됨
        }
    }