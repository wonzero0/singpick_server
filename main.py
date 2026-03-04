from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models
from database import engine, get_db
from routers import booth, users, songs, library 
from fastapi.staticfiles import StaticFiles

# DB 테이블 생성
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# /kiosk 주소로 접근 가능
app.mount("/kiosk", StaticFiles(directory="kiosk"), name="kiosk")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 곳에서 접속 허용
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST 등 모든 방식 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# 라우터 연결
app.include_router(users.router)
app.include_router(booth.router)
app.include_router(songs.router)
app.include_router(library.router) # [추가]

# 임시 노래 데이터 10곡 넣기 (서버 켤 때 자동 실행)
def init_dummy_songs(db: Session):
    if db.query(models.Song).count() == 0: # 노래가 하나도 없으면
        dummy_songs = [
            models.Song(title="0+0", singer="한로로", tj_number=99991),
            models.Song(title="한숨", singer="이하이", tj_number=99992),
            models.Song(title="여름밤에 우리", singer="전진희(feat. wave to earth)", tj_number=99993),
            models.Song(title="좋은 날", singer="아이유", tj_number=1001),
            models.Song(title="너랑 나", singer="아이유", tj_number=1002),
            models.Song(title="밤편지", singer="아이유", tj_number=1003),
            models.Song(title="보고 싶다", singer="김범수", tj_number=2001),
            models.Song(title="응급실", singer="izi", tj_number=3001),
            models.Song(title="소주 한 잔", singer="임창정", tj_number=4001),
            models.Song(title="Hype Boy", singer="NewJeans", tj_number=5001),
            models.Song(title="Ditto", singer="NewJeans", tj_number=5002),
            models.Song(title="ETA", singer="NewJeans", tj_number=5003),
            models.Song(title="Dynamite", singer="BTS", tj_number=6001),
        ]
        db.add_all(dummy_songs)
        db.commit()
        print("🎵 [System] 가짜 노래 10곡이 DB에 저장되었습니다!")

# 서버 시작 시 실행되는 이벤트
@app.on_event("startup")
def on_startup():
    db = next(get_db())
    init_dummy_songs(db)

@app.get("/")
def read_root():
    return {"message": "SingPick Server is Running!"}