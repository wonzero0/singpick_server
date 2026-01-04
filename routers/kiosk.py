from fastapi import APIRouter
from pydantic import BaseModel

# 이 파일은 '키오스크' 관련 기능만 모아두는 곳입니다.
router = APIRouter(prefix="/kiosk", tags=["External Kiosk (외부 키오스크)"])

# 요청 데이터 양식 (곡 수 선택)
class SongSelect(BaseModel):
    user_email: str | None = None  # 비회원이면 None(비어있음)
    song_count: int  # 1 ~ 3곡

# 1. 잔여 곡 수 / 회원 상태 확인 API
@router.get("/user/{email}")
def check_user_credits(email: str):
    # 나중에 여기에 DB 연결 코드가 들어갑니다.
    # 지금은 테스트용으로 무조건 0곡 남았다고 알려줍시다.
    return {
        "email": email,
        "is_member": True,
        "remaining_songs": 0  # 잔여 곡 수
    }

# 2. 곡 수 결제 및 입장 처리 API
@router.post("/entry")
def enter_booth(selection: SongSelect):
    # [cite_start]설계서 SFR-AD-1: 회원/비회원 구분하여 곡 수 설정 [cite: 121]
    user_type = "회원" if selection.user_email else "비회원"
    
    return {
        "status": "success",
        "message": f"{user_type} 입장 처리 완료",
        "data": {
            "assigned_songs": selection.song_count,
            "room_status": "active" # 부스 활성화
        }
    }