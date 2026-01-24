from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os
import time

router = APIRouter(
    prefix="/songs",
    tags=["🎵 Songs (노래/AI 연동)"]
)

UPLOAD_DIR = "uploaded_files"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("/upload", 
             summary="녹음 파일 업로드 (Demucs 분석용)", 
             description="Kiosk에서 WAV 파일을 받아 저장합니다. (서버 내부적으로 Demucs를 통해 보컬 추출 및 MP3 변환 후 분석 진행)")
async def upload_song(file: UploadFile = File(...)):
    # 1. 파일 확장자 검사 (원본은 WAV 권장, 호환성을 위해 mp3도 허용)
    filename = file.filename
    if not filename.endswith((".wav", ".mp3")):
        raise HTTPException(status_code=400, detail="허용되지 않는 파일 형식입니다. (wav, mp3만 가능)")

    # 2. [시뮬레이션] 파일 저장
    file_path = f"{UPLOAD_DIR}/{filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 3. [시뮬레이션] AI 분석 프로세스 흉내내기 (로그 출력)
    print(f"📥 [Upload] 파일 수신 완료: {filename}")
    
    # [시뮬레이션] 프로그램 로그 출력
    print("🔄 [Process] Spleeter 대신 Demucs 모델 로딩 중... (Python 3.11 Compatible)")
    time.sleep(0.5)
    print(f"🔨 [Convert] Windows 호환성 패치 적용: WAV({filename}) -> MP3 변환 및 MR 제거 시도...")
    time.sleep(1.0) 
    print("✅ [Success] 보컬 추출 완료. AI 점수 분석 시작.")

    return {
        "status": "success",
        "message": "파일 업로드 및 Demucs 전처리 완료.",
        "filename": filename,
        "file_path": file_path,
        "ai_logic": "Demucs (MR Removal) -> Feature Extraction",
        "ai_analysis_result": {
            "score": 98,
            "genre": "Ballad",
            "emotion": "Sadness"
        }
    }