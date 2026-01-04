from fastapi import APIRouter
from pydantic import BaseModel

# 이 파일은 '부스 내부' 기능만 모아두는 곳입니다.
# [중요] 여기에 'import kiosk' 같은 게 있으면 안 됩니다!

router = APIRouter(prefix="/booth", tags=["Internal Booth (내부 부스)"])

# 분석 요청 데이터 양식
class AnalyzeRequest(BaseModel):
    user_email: str | None = None
    song_title: str
    audio_file_path: str  # 녹음된 파일 위치 (나중에 실제 파일 전송으로 변경)

# 1. 가사 불러오기 API
@router.get("/lyrics/{song_title}")
def get_lyrics(song_title: str):
    # 나중에 DB에서 진짜 가사를 가져옵니다.
    return {
        "song": song_title,
        "lyrics": [
            {"time": 12.5, "text": "가사 첫 줄 예시"},
            {"time": 18.2, "text": "가사 두 번째 줄 예시"}
        ]
    }

# 2. AI 분석 요청 API
@router.post("/analyze")
def analyze_song(request: AnalyzeRequest):
    # 여기서 3번 팀원의 AI 코드를 호출하게 됩니다.
    return {
        "status": "processing",
        "message": "AI 분석이 시작되었습니다.",
        "result": {
            "score": 95,          # 임시 점수
            "pitch_accuracy": "High",
            "feedback": "고음 처리가 아주 좋습니다!" # 회원 데이터 업데이트용 피드백
        }
    }