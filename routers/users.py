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
@router.post("/login", summary="로그인")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    # 1. 입력받은 전화번호를 암호화
    crypto_phone = aes_encrypt(user_data.user_id) 
    
    # 2. 암호화된 전화번호로 유저 조회
    db_user = db.query(models.User).filter(models.User.phone == crypto_phone).first()
    
    # 3. 유저가 없거나 비밀번호(해시)가 틀리면 에러
    if not db_user or not pwd_context.verify(user_data.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="전화번호 또는 비밀번호가 일치하지 않습니다."
        )
    
    return {
        "status": "success",
        "message": f"안녕하세요, {db_user.user_id}님!",
        "user_id": db_user.user_id
    }

# 4. 로그인 API (routers/users.py)
@router.post("/login", summary="로그인")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    try:
        from utils import aes_encrypt 
        crypto_phone = aes_encrypt(user_data.user_id) 

        # 암호화된 전화번호로 유저를 찾습니다.
        db_user = db.query(models.User).filter(models.User.phone == crypto_phone).first()
        
        # 유저가 없거나 비밀번호가 틀린 경우
        if not db_user or not pwd_context.verify(user_data.password, db_user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="전화번호 또는 비밀번호가 일치하지 않습니다."
            )
        
        return {
            "status": "success",
            "message": f"안녕하세요, {db_user.user_id}님!",
            "user_id": db_user.user_id
        }
    except Exception as e:
        print(f"서버 내부 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))
# 5. 내 기록 조회 (기존 코드 유지)
@router.get("/{user_id}/history", summary="내 점수 기록 조회")
def get_user_history(user_id: str, db: Session = Depends(get_db)):
    history = db.query(models.AnalysisResult)\
                .filter(models.AnalysisResult.user_id == user_id)\
                .order_by(models.AnalysisResult.id.desc())\
                .all()
    return {"status": "success", "data": history}