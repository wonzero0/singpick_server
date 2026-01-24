from sqlalchemy import Column, Integer, String, Boolean
from database import Base

# 1. 사용자 테이블
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)      
    user_id = Column(String(50))                            
    phone = Column(String(100), unique=True, index=True)     
    password = Column(String(100))                          

# 2. 노래방 부스(방) 테이블
class Booth(Base):
    __tablename__ = "booths"

    booth_id = Column(Integer, primary_key=True, index=True) # 방 번호 (1, 2, 3...)
    name = Column(String(50))                                # 방 이름
    status = Column(String(20), default="empty")             # 상태 (empty, busy)

# 3. 노래 데이터 (노래방 책)
class Song(Base):
    __tablename__ = "songs"

    song_id = Column(Integer, primary_key=True, index=True) # 고유 번호 (1001, 1002...)
    title = Column(String(100), index=True)                 # 노래 제목 (좋은 날)
    singer = Column(String(50), index=True)                 # 가수 (아이유)
    tj_number = Column(Integer, unique=True)                # TJ 노래방 번호 (가짜)

# 4. 예약 목록 (부스별 대기열)
class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    booth_id = Column(Integer)  # 어느 방에서 예약했는지
    song_id = Column(Integer)   # 어떤 노래인지
    status = Column(String(20), default="waiting") # waiting(대기), playing(재생중)