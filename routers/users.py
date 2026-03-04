from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, field_validator
from database import get_db
import models
from utils import aes_encrypt 
from passlib.context import CryptContext

# 1. 보안 설정: 비밀번호 암호화 컨텍스트 (한 번만 선언)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

class UserLogin(BaseModel):
    user_id: str
    password: str

# 3. 회원가입 API 
@router.post("/signup", summary="회원가입")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # 중복 체크
    if db.query(models.User).filter(models.User.user_id == user.user_id).first():
        raise HTTPException(status_code=400, detail="이미 존재하는 아이디입니다.")

    # [보안 적용] 비밀번호는 해시화, 전화번호는 AES 암호화
    hashed_password = pwd_context.hash(user.password)
    crypto_phone = aes_encrypt(user.phone)

    new_user = models.User(
        user_id=user.user_id,
        phone=crypto_phone,
        password=hashed_password
    )
    db.add(new_user)
    db.commit()
    return {"status": "success", "message": "회원가입이 완료되었습니다."}

# 4. 로그인 API
@router.post("/login", summary="로그인")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.user_id == user_data.user_id).first()
    
    # [보안 적용] 암호화된 비밀번호와 입력값을 안전하게 비교
    if not db_user or not pwd_context.verify(user_data.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 일치하지 않습니다."
        )
    
    return {
        "status": "success",
        "message": f"안녕하세요, {db_user.user_id}님!",
        "user_info": {"user_id": db_user.user_id}
    }

# 5. 내 기록 조회 (기존 코드 유지)
@router.get("/{user_id}/history", summary="내 점수 기록 조회")
def get_user_history(user_id: str, db: Session = Depends(get_db)):
    history = db.query(models.AnalysisResult)\
                .filter(models.AnalysisResult.user_id == user_id)\
                .order_by(models.AnalysisResult.id.desc())\
                .all()
    return {"status": "success", "data": history}